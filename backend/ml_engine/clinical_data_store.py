import json
import logging
import os
from dataclasses import dataclass
from typing import Dict, List

from django.conf import settings

logger = logging.getLogger('health_ai')


@dataclass
class ClinicalDataStore:
    knowledge_base: List[Dict]
    condition_recommendations: List[Dict]
    medication_safety: List[Dict]
    specialist_mapping: List[Dict]
    emergency_rules: List[Dict]
    nutrition_dataset: List[Dict]


_DATA_STORE: ClinicalDataStore | None = None


def _load_json_file(path: str, fallback: List[Dict], file_label: str) -> List[Dict]:
    if path and os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as file_handle:
            data = json.load(file_handle)
        if isinstance(data, list):
            logger.info('Loaded %s entries from %s', len(data), file_label)
            return data
        logger.warning('%s is not a list. Using fallback.', file_label)
    else:
        logger.warning('%s not found at %s. Using fallback.', file_label, path)
    return fallback


def _build_store() -> ClinicalDataStore:
    model_paths = settings.ML_MODELS
    return ClinicalDataStore(
        knowledge_base=_load_json_file(
            model_paths.get('KNOWLEDGE_BASE_PATH', ''),
            fallback=[],
            file_label='knowledge_base.json',
        ),
        condition_recommendations=_load_json_file(
            model_paths.get('CONDITION_RECOMMENDATIONS_PATH', ''),
            fallback=[],
            file_label='condition_recommendations.json',
        ),
        medication_safety=_load_json_file(
            model_paths.get('MEDICATION_SAFETY_PATH', ''),
            fallback=[],
            file_label='medication_safety.json',
        ),
        specialist_mapping=_load_json_file(
            model_paths.get('SPECIALIST_MAPPING_PATH', ''),
            fallback=[],
            file_label='specialist_mapping.json',
        ),
        emergency_rules=_load_json_file(
            model_paths.get('EMERGENCY_RULES_PATH', ''),
            fallback=[],
            file_label='emergency_rules.json',
        ),
        nutrition_dataset=_load_json_file(
            model_paths.get('NUTRITION_DATASET_PATH', ''),
            fallback=[],
            file_label='nutrition_dataset.json',
        ),
    )


def get_clinical_data_store() -> ClinicalDataStore:
    global _DATA_STORE
    if _DATA_STORE is None:
        _DATA_STORE = _build_store()
    return _DATA_STORE


def warmup_clinical_data_store() -> None:
    get_clinical_data_store()
