"""Stabilized symptom classifier for deterministic production behavior."""
import json
import logging
from pathlib import Path
from typing import Dict, Tuple

from .constants import (
    CONDITION_KEYWORD_MAP,
    EMERGENCY_KEYWORDS,
    MASTER_CONDITION_LIST,
    normalize_condition,
    safe_float,
)

logger = logging.getLogger('health_ai')

HIGH_RISK_KEYWORDS = [
    'blood', 'severe', 'sudden', 'extreme', 'unbearable',
    'persistent', 'worsening', 'high fever', 'vomiting blood',
    'black stool', 'difficulty breathing'
]


class SymptomClassifier:
    """
    Stabilized ClinicalBERT classifier.
    Guarantees a valid whitelisted condition is always returned.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._label_classes = list(MASTER_CONDITION_LIST)
        self._confidence_threshold = 0.60
        self._device = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy load ClinicalBERT model."""
        if self._model_loaded:
            return
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            from django.conf import settings

            project_root = Path(__file__).resolve().parents[2]
            local_model_path = project_root / 'ml' / 'clinicalbert_model'
            configured_path = settings.ML_MODELS.get('SYMPTOM_CLASSIFIER', str(local_model_path))
            model_name = configured_path if configured_path else str(local_model_path)

            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                model_name
            )
            self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self._model.to(self._device)

            classes_path = Path(model_name) / 'label_classes.json'
            if classes_path.exists():
                with open(classes_path, 'r', encoding='utf-8') as file_handle:
                    loaded_classes = json.load(file_handle)
                if isinstance(loaded_classes, list) and loaded_classes:
                    self._label_classes = [normalize_condition(label) for label in loaded_classes]

            model_labels = max(1, int(getattr(self._model.config, 'num_labels', len(self._label_classes))))
            aligned = [
                self._label_classes[index] if index < len(self._label_classes) else MASTER_CONDITION_LIST[index % len(MASTER_CONDITION_LIST)]
                for index in range(model_labels)
            ]
            self._label_classes = aligned
            self._model.config.id2label = {index: label for index, label in enumerate(self._label_classes)}
            self._model.config.label2id = {label: index for index, label in enumerate(self._label_classes)}

            self._model.eval()
            logger.info(f'ClinicalBERT loaded: {model_name}')
        except Exception as e:
            logger.warning(f'ClinicalBERT not available, using rule-based classifier: {e}')
        self._model_loaded = True

    def classify(self, symptom_text: str) -> Tuple[str, float, str]:
        """
        Classify symptoms and return (category, confidence, risk_level).
        """
        text_lower = str(symptom_text or '').lower().strip()
        if not text_lower:
            return 'common_cold', 0.0, 'LOW'

        if self._is_emergency_text(text_lower):
            emergency_condition, emergency_conf = self._keyword_condition(text_lower)
            return emergency_condition, emergency_conf, 'CRITICAL'

        self._load_model()

        if self._model is not None:
            try:
                model_condition, model_confidence = self._safe_predict(text_lower)
                if model_confidence >= self._confidence_threshold and model_condition in MASTER_CONDITION_LIST:
                    return model_condition, safe_float(model_confidence, 0.0), self._assess_risk(text_lower)
            except Exception as e:
                logger.warning(f'Model inference failed, using keyword fallback: {e}')

        fallback_condition, fallback_conf = self._keyword_condition(text_lower)
        return fallback_condition, safe_float(fallback_conf, 0.0), self._assess_risk(text_lower)

    def _safe_predict(self, text: str) -> Tuple[str, float]:
        """Safe model prediction with deterministic label validation."""
        import torch
        inputs = self._tokenizer(
            text,
            return_tensors='pt',
            max_length=256,
            truncation=True,
            padding=True
        )
        inputs = {key: value.to(self._device) for key, value in inputs.items()}
        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            pred_idx = torch.argmax(probs).item()
            confidence = probs[0][pred_idx].item()

        categories = self._label_classes or list(MASTER_CONDITION_LIST)
        raw_category = categories[pred_idx] if pred_idx < len(categories) else 'common_cold'
        category = normalize_condition(raw_category)
        return category, safe_float(confidence, default=0.0)

    def _keyword_condition(self, text: str) -> Tuple[str, float]:
        scores: Dict[str, int] = {condition: 0 for condition in MASTER_CONDITION_LIST}
        for category, keywords in CONDITION_KEYWORD_MAP.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1

        best_category = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        confidence = scores[best_category] / max(total_matches, 1) if total_matches else 0.5

        if scores[best_category] == 0:
            best_category = 'common_cold'
            confidence = 0.5

        return normalize_condition(best_category), safe_float(confidence, default=0.5)

    @staticmethod
    def _is_emergency_text(text: str) -> bool:
        return any(keyword in text for keyword in EMERGENCY_KEYWORDS)

    def _assess_risk(self, text: str) -> str:
        """Assess risk level from symptom text."""
        if self._is_emergency_text(text):
            return 'CRITICAL'
        high_count = sum(1 for kw in HIGH_RISK_KEYWORDS if kw in text)
        if high_count >= 2:
            return 'HIGH'
        if high_count == 1:
            return 'MEDIUM'
        return 'LOW'


_classifier_instance = None


def get_classifier() -> SymptomClassifier:
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = SymptomClassifier()
    return _classifier_instance
