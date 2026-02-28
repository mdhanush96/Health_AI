import logging
from typing import Dict, List

from .clinical_data_store import get_clinical_data_store
from .constants import (
    RECOMMENDATION_ALIAS_MAP,
    default_safe_response,
    normalize_condition,
    safe_string_list,
)
from .emergency_rule_engine import get_emergency_rule_engine

logger = logging.getLogger('health_ai')


class ClinicalDecisionEngine:
    def __init__(self):
        self._store = get_clinical_data_store()
        self._emergency_engine = get_emergency_rule_engine()
        self._condition_lookup = {
            item.get('condition', '').lower(): item
            for item in self._store.condition_recommendations
        }
        self._specialist_lookup = {
            item.get('condition', '').lower(): item.get('specialist', 'General Physician')
            for item in self._store.specialist_mapping
        }
        self._medication_lookup = {
            item.get('name', '').lower(): item
            for item in self._store.medication_safety
        }

    def generate_recommendation(self, symptom_text: str, condition: str, severity: str) -> Dict:
        condition_normalized = normalize_condition(condition)
        severity_normalized = str(severity or 'low').lower()

        emergency_result = self._emergency_engine.evaluate(symptom_text, condition_normalized, severity_normalized)
        if emergency_result.get('emergency'):
            base = default_safe_response(condition=condition_normalized, confidence=0.0)
            base.update({
                'emergency': True,
                'severity': emergency_result['severity'],
                'action': emergency_result['action'],
                'specialist': emergency_result['specialist'],
                'emergency_flag': True,
            })
            return base

        recommendation_key = RECOMMENDATION_ALIAS_MAP.get(condition_normalized, condition_normalized)
        recommendation = self._condition_lookup.get(recommendation_key) or {}
        candidate_meds = safe_string_list(recommendation.get('otc_candidates', []))
        red_flags = set(emergency_result.get('red_flags', []))

        safe_otc = self._validate_medication_safety(
            candidate_meds=candidate_meds,
            condition=condition_normalized,
            severity=severity_normalized,
            red_flags=red_flags,
        )

        nutrition_items = self._nutrition_for_condition(condition_normalized)

        result = default_safe_response(condition=condition_normalized, confidence=0.0)
        result.update({
            'condition': condition_normalized,
            'severity': severity_normalized,
            'emergency': False,
            'emergency_flag': False,
            'diet': safe_string_list(recommendation.get('diet', [])) + nutrition_items,
            'exercise': safe_string_list(recommendation.get('exercise', [])),
            'lifestyle': safe_string_list(recommendation.get('lifestyle', [])),
            'safe_otc': safe_string_list(safe_otc),
            'specialist': self._specialist_lookup.get(recommendation_key, 'General Physician'),
        })
        if not result['diet']:
            result['diet'] = ['Hydration-focused meals and balanced nutrition.']
        if not result['exercise']:
            result['exercise'] = ['Light activity as tolerated and adequate rest.']
        if not result['lifestyle']:
            result['lifestyle'] = ['Monitor symptoms and seek medical review if worsening.']
        return result

    def _nutrition_for_condition(self, condition: str, limit: int = 5) -> List[str]:
        collected: List[str] = []
        for item in self._store.nutrition_dataset:
            targets = [entry.lower() for entry in item.get('recommended_for', [])]
            if condition in targets or 'general' in targets:
                collected.append(f"{item.get('item', 'food')}: {item.get('benefit', 'Nutritional support')}")
            if len(collected) >= limit:
                break
        return collected

    def _validate_medication_safety(
        self,
        candidate_meds: List[str],
        condition: str,
        severity: str,
        red_flags: set,
    ) -> List[str]:
        safe_medications: List[str] = []

        for med_name in candidate_meds:
            med = self._medication_lookup.get(med_name.lower())
            if not med:
                continue

            allowed_severity = [value.lower() for value in med.get('allowed_severity', [])]
            contraindications = [value.lower() for value in med.get('contraindicated_conditions', [])]
            avoid_red_flags = [value.lower() for value in med.get('avoid_with_red_flags', [])]

            if severity not in allowed_severity:
                continue
            if condition in contraindications:
                continue
            if red_flags.intersection(set(avoid_red_flags)):
                continue

            safe_medications.append(med_name)

        return safe_medications


_CLINICAL_DECISION_ENGINE = None


def get_clinical_decision_engine() -> ClinicalDecisionEngine:
    global _CLINICAL_DECISION_ENGINE
    if _CLINICAL_DECISION_ENGINE is None:
        _CLINICAL_DECISION_ENGINE = ClinicalDecisionEngine()
    return _CLINICAL_DECISION_ENGINE
