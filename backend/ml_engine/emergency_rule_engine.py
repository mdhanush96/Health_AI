import logging
from typing import Dict, Set

from .clinical_data_store import get_clinical_data_store
from .constants import EMERGENCY_KEYWORDS

logger = logging.getLogger('health_ai')


class EmergencyRuleEngine:
    def __init__(self):
        self._store = get_clinical_data_store()

    @staticmethod
    def _normalize_token(value: str) -> str:
        return value.strip().lower().replace(' ', '_')

    def extract_red_flags(self, symptom_text: str) -> Set[str]:
        text = symptom_text.lower()
        red_flags: Set[str] = set()
        for rule in self._store.emergency_rules:
            for keyword in rule.get('keywords', []):
                if keyword.lower() in text:
                    red_flags.add(self._normalize_token(keyword))
        return red_flags

    def evaluate(self, symptom_text: str, condition: str, severity: str) -> Dict:
        text = symptom_text.lower()
        red_flags = self.extract_red_flags(symptom_text)

        for rule in self._store.emergency_rules:
            for keyword in rule.get('keywords', []):
                if keyword.lower() in text:
                    return {
                        'emergency': True,
                        'severity': rule.get('severity', 'critical'),
                        'action': rule.get('action', 'Immediate ER Visit'),
                        'specialist': rule.get('specialist', 'Emergency Medicine'),
                        'matched_rule': rule.get('rule_id', ''),
                        'red_flags': sorted(red_flags),
                    }

        for keyword in EMERGENCY_KEYWORDS:
            if keyword in text:
                return {
                    'emergency': True,
                    'severity': 'critical',
                    'action': 'Immediate ER Visit',
                    'specialist': self._get_specialist_for_condition(condition),
                    'matched_rule': 'global_keyword_override',
                    'red_flags': sorted(red_flags | {self._normalize_token(keyword)}),
                }

        return {
            'emergency': False,
            'severity': str(severity).lower() or 'low',
            'red_flags': sorted(red_flags),
        }

    def _get_specialist_for_condition(self, condition: str) -> str:
        condition_normalized = condition.lower()
        for mapping in self._store.specialist_mapping:
            if mapping.get('condition', '').lower() == condition_normalized:
                return mapping.get('specialist', 'General Physician')
        return 'General Physician'


_EMERGENCY_ENGINE_INSTANCE = None


def get_emergency_rule_engine() -> EmergencyRuleEngine:
    global _EMERGENCY_ENGINE_INSTANCE
    if _EMERGENCY_ENGINE_INSTANCE is None:
        _EMERGENCY_ENGINE_INSTANCE = EmergencyRuleEngine()
    return _EMERGENCY_ENGINE_INSTANCE
