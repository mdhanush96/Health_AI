import logging
import importlib
import re
from functools import lru_cache
from typing import Dict, List

logger = logging.getLogger('health_ai')


@lru_cache(maxsize=1)
def _get_ner_pipeline():
    from django.conf import settings

    model_name = settings.ML_MODELS.get('NER_MODEL', 'dmis-lab/biobert-base-cased-v1.1')
    pipeline = importlib.import_module('transformers').pipeline
    return pipeline('ner', model=model_name, aggregation_strategy='simple')


class BioBERTNER:
    def extract(self, text: str) -> Dict:
        try:
            ner_pipeline = _get_ner_pipeline()
            entities = ner_pipeline(text[:4000])
        except Exception as exc:
            logger.warning('BioBERT NER unavailable, using regex fallback: %s', exc)
            entities = []

        diseases: List[str] = []
        medications: List[str] = []
        lab_values: List[str] = []

        for entity in entities:
            token = str(entity.get('word', '')).strip()
            token_lower = token.lower()
            if any(keyword in token_lower for keyword in ['diabetes', 'hypertension', 'asthma', 'infection', 'stroke']):
                diseases.append(token)
            if any(keyword in token_lower for keyword in ['acetam', 'ibuprofen', 'metformin', 'insulin', 'statin']):
                medications.append(token)

        lab_pattern = re.compile(r'\b(?:hba1c|ldl|hdl|wbc|rbc|hemoglobin|creatinine|glucose)\b\s*[:=]?\s*[\d.]+', re.IGNORECASE)
        lab_values.extend(lab_pattern.findall(text))

        return {
            'raw_entities': entities,
            'diseases': sorted(set(diseases)),
            'medications': sorted(set(medications)),
            'lab_values': sorted(set(lab_values)),
        }


_ner_instance = None


def get_ner_extractor() -> BioBERTNER:
    global _ner_instance
    if _ner_instance is None:
        _ner_instance = BioBERTNER()
    return _ner_instance
