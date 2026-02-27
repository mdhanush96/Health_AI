"""
Symptom Classifier using ClinicalBERT.
Performs multi-class symptom classification and risk assessment.
"""
import logging
import re
from typing import Tuple

logger = logging.getLogger('health_ai')

# Symptom categories mapped to conditions
SYMPTOM_CATEGORIES = {
    'cardiovascular': [
        'chest pain', 'palpitations', 'shortness of breath', 'edema',
        'hypertension', 'tachycardia', 'bradycardia', 'arrhythmia',
        'heart attack', 'angina', 'claudication'
    ],
    'respiratory': [
        'cough', 'wheezing', 'dyspnea', 'breathlessness', 'hemoptysis',
        'pneumonia', 'bronchitis', 'asthma', 'copd', 'pleurisy'
    ],
    'neurological': [
        'headache', 'dizziness', 'seizure', 'numbness', 'tingling',
        'confusion', 'memory loss', 'tremor', 'migraine', 'stroke',
        'vertigo', 'syncope'
    ],
    'gastrointestinal': [
        'nausea', 'vomiting', 'diarrhea', 'constipation', 'abdominal pain',
        'bloating', 'heartburn', 'dysphagia', 'jaundice', 'blood in stool'
    ],
    'musculoskeletal': [
        'joint pain', 'back pain', 'muscle weakness', 'stiffness',
        'arthritis', 'fracture', 'swelling', 'tenderness'
    ],
    'endocrine': [
        'fatigue', 'weight gain', 'weight loss', 'excessive thirst',
        'frequent urination', 'diabetes', 'thyroid', 'hormonal'
    ],
    'dermatological': [
        'rash', 'itching', 'hives', 'eczema', 'psoriasis', 'acne',
        'lesion', 'discoloration', 'wound'
    ],
    'infectious': [
        'fever', 'chills', 'night sweats', 'infection', 'inflammation',
        'virus', 'bacteria', 'fungal', 'covid', 'flu', 'cold'
    ],
    'psychiatric': [
        'anxiety', 'depression', 'insomnia', 'stress', 'panic',
        'hallucination', 'suicidal', 'bipolar', 'ptsd', 'ocd'
    ],
}

EMERGENCY_KEYWORDS = [
    'chest pain', 'heart attack', 'stroke', 'cannot breathe',
    'unconscious', 'seizure', 'severe bleeding', 'anaphylaxis',
    'suicidal', 'overdose', 'poisoning', 'high fever above 104',
    'shortness of breath severe', 'crushing chest'
]

HIGH_RISK_KEYWORDS = [
    'blood', 'severe', 'sudden', 'extreme', 'unbearable',
    'persistent', 'worsening', 'high fever', 'vomiting blood',
    'black stool', 'difficulty breathing'
]


class SymptomClassifier:
    """
    Rule-based symptom classifier with optional ClinicalBERT integration.
    Falls back gracefully if transformer models are unavailable.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._model_loaded = False

    def _load_model(self):
        """Lazy load ClinicalBERT model."""
        if self._model_loaded:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            from django.conf import settings
            model_name = settings.ML_MODELS.get('SYMPTOM_CLASSIFIER', 'emilyalsentzer/Bio_ClinicalBERT')
            self._tokenizer = AutoTokenizer.from_pretrained(model_name)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                model_name, num_labels=len(SYMPTOM_CATEGORIES)
            )
            self._model.eval()
            logger.info(f'ClinicalBERT loaded: {model_name}')
        except Exception as e:
            logger.warning(f'ClinicalBERT not available, using rule-based classifier: {e}')
        self._model_loaded = True

    def classify(self, symptom_text: str) -> Tuple[str, float, str]:
        """
        Classify symptoms and return (category, confidence, risk_level).
        """
        self._load_model()
        text_lower = symptom_text.lower()

        # Try transformer-based classification first
        if self._model is not None:
            try:
                return self._classify_with_model(text_lower)
            except Exception as e:
                logger.warning(f'Model inference failed, falling back to rules: {e}')

        # Rule-based fallback
        return self._classify_rule_based(text_lower)

    def _classify_with_model(self, text: str) -> Tuple[str, float, str]:
        """Classify using ClinicalBERT."""
        import torch
        inputs = self._tokenizer(
            text,
            return_tensors='pt',
            max_length=256,
            truncation=True,
            padding=True
        )
        with torch.no_grad():
            outputs = self._model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            pred_idx = torch.argmax(probs).item()
            confidence = probs[0][pred_idx].item()

        categories = list(SYMPTOM_CATEGORIES.keys())
        category = categories[pred_idx] if pred_idx < len(categories) else 'general'
        risk_level = self._assess_risk(text)
        return category, round(confidence, 4), risk_level

    def _classify_rule_based(self, text: str) -> Tuple[str, float, str]:
        """Keyword-based symptom classification."""
        scores = {cat: 0 for cat in SYMPTOM_CATEGORIES}
        for category, keywords in SYMPTOM_CATEGORIES.items():
            for keyword in keywords:
                if keyword in text:
                    scores[category] += 1

        best_category = max(scores, key=scores.get)
        total_matches = sum(scores.values())
        confidence = scores[best_category] / max(total_matches, 1)

        if scores[best_category] == 0:
            best_category = 'general'
            confidence = 0.5

        risk_level = self._assess_risk(text)
        return best_category, round(confidence, 4), risk_level

    def _assess_risk(self, text: str) -> str:
        """Assess risk level from symptom text."""
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in text:
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
