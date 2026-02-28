from math import isfinite
from typing import Dict, List

MASTER_CONDITION_LIST: List[str] = [
    'cardiac_issue',
    'type_2_diabetes',
    'hypertension',
    'common_cold',
    'migraine',
    'anxiety_disorder',
    'arthritis',
    'asthma',
    'gastritis',
    'dermatology_issue',
]

CONDITION_KEYWORD_MAP: Dict[str, List[str]] = {
    'cardiac_issue': ['chest pain', 'palpitations', 'heart', 'angina', 'cardiac', 'pressure in chest'],
    'type_2_diabetes': ['frequent urination', 'polyuria', 'excessive thirst', 'high sugar', 'diabetes', 'blurred vision'],
    'hypertension': ['high blood pressure', 'hypertension', 'bp high', 'elevated bp'],
    'common_cold': ['runny nose', 'sore throat', 'cold', 'cough', 'sneezing', 'nasal congestion'],
    'migraine': ['migraine', 'headache', 'photophobia', 'aura', 'throbbing pain'],
    'anxiety_disorder': ['anxiety', 'panic', 'restlessness', 'insomnia', 'worry', 'stress'],
    'arthritis': ['joint pain', 'stiffness', 'arthritis', 'knee pain', 'swollen joint'],
    'asthma': ['wheezing', 'asthma', 'shortness of breath', 'breathlessness', 'chest tightness'],
    'gastritis': ['acidity', 'heartburn', 'gastritis', 'abdominal pain', 'nausea', 'bloating'],
    'dermatology_issue': ['rash', 'itching', 'eczema', 'hives', 'skin lesion', 'dermatitis'],
}

EMERGENCY_KEYWORDS: List[str] = [
    'chest pain', 'crushing chest', 'cannot breathe', 'severe shortness of breath',
    'slurred speech', 'facial droop', 'one side weak', 'unconscious',
    'vomiting blood', 'blood in stool', 'black stool', 'severe bleeding',
    'anaphylaxis', 'throat swelling', 'seizure', 'overdose', 'poisoning',
]

CONDITION_ALIAS_MAP: Dict[str, str] = {
    'cardiovascular': 'cardiac_issue',
    'endocrine': 'type_2_diabetes',
    'infectious': 'common_cold',
    'respiratory': 'asthma',
    'psychiatric': 'anxiety_disorder',
    'musculoskeletal': 'arthritis',
    'gastrointestinal': 'gastritis',
    'dermatological': 'dermatology_issue',
    'neurological': 'migraine',
}

RECOMMENDATION_ALIAS_MAP: Dict[str, str] = {
    'cardiac_issue': 'cardiovascular',
    'type_2_diabetes': 'type_2_diabetes',
    'hypertension': 'hypertension',
    'common_cold': 'infectious',
    'migraine': 'migraine',
    'anxiety_disorder': 'psychiatric',
    'arthritis': 'musculoskeletal',
    'asthma': 'asthma',
    'gastritis': 'gastrointestinal',
    'dermatology_issue': 'dermatological',
}


def normalize_condition(value: str) -> str:
    normalized = str(value or '').strip().lower()
    if normalized in MASTER_CONDITION_LIST:
        return normalized
    if normalized in CONDITION_ALIAS_MAP:
        return CONDITION_ALIAS_MAP[normalized]
    return 'common_cold'


def safe_float(value, default: float = 0.0) -> float:
    try:
        numeric_value = float(value)
        if isfinite(numeric_value):
            return round(numeric_value, 4)
    except Exception:
        pass
    return default


def safe_string_list(values) -> List[str]:
    if not values:
        return []
    return [str(item) for item in values if str(item).strip()]


def default_safe_response(condition: str = 'common_cold', confidence: float = 0.0) -> Dict:
    safe_condition = normalize_condition(condition)
    return {
        'condition': safe_condition,
        'confidence': safe_float(confidence, default=0.0),
        'diet': ['Hydration-focused meals and balanced nutrition.'],
        'exercise': ['Light activity as tolerated and adequate rest.'],
        'lifestyle': ['Monitor symptoms and seek medical review if worsening.'],
        'safe_otc': [],
        'specialist': 'General Physician',
        'emergency_flag': False,
        'explanation': (
            'This is a safety fallback response. Please consult a qualified clinician '
            'for persistent or worsening symptoms.'
        ),
        'severity': 'low',
        'emergency': False,
    }
