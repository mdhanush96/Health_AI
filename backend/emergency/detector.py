"""
Emergency severity detection system.
Multi-level emergency assessment with keyword and pattern matching.
"""
from typing import Dict, List, Tuple

# Emergency severity rules (ordered by priority)
EMERGENCY_RULES = [
    {
        'severity': 'CRITICAL',
        'keywords': [
            'chest pain', 'heart attack', 'cardiac arrest',
            'cannot breathe', "can't breathe", 'not breathing',
            'stroke', 'facial droop', 'arm weakness', 'slurred speech',
            'unconscious', 'unresponsive', 'collapsed',
            'severe bleeding', 'uncontrolled bleeding',
            'anaphylaxis', 'anaphylactic shock', 'throat closing',
            'suicidal', 'suicide', 'want to die', 'overdose',
            'poisoning', 'severe head injury', 'spinal injury',
            'pulmonary embolism', 'severe allergic reaction',
            'diabetic coma', 'seizure not stopping', 'status epilepticus',
        ],
        'action': (
            'CALL 911 IMMEDIATELY. This is a life-threatening emergency. '
            'Do not drive yourself. Stay calm and follow dispatcher instructions.'
        ),
        'contact': '911',
    },
    {
        'severity': 'HIGH',
        'keywords': [
            'high fever', 'fever above 104', 'fever 40',
            'difficulty breathing', 'shortness of breath',
            'severe abdominal pain', 'sudden severe headache',
            'vomiting blood', 'blood in stool', 'black tarry stool',
            'severe chest pressure', 'severe dizziness',
            'confusion', 'disorientation', 'altered mental status',
            'broken bone', 'possible fracture', 'deep cut',
            'severe burn', 'eye injury',
        ],
        'action': (
            'Go to the Emergency Room or Urgent Care immediately. '
            'Call a trusted person to take you. Do not wait - seek care today.'
        ),
        'contact': '911 or nearest ER',
    },
    {
        'severity': 'MEDIUM',
        'keywords': [
            'persistent fever', 'fever for more than 3 days',
            'moderate pain', 'worsening symptoms',
            'urinary tract infection symptoms', 'ear pain',
            'rash spreading', 'swollen lymph nodes',
            'persistent cough', 'vomiting repeatedly',
            'dehydration signs', 'blood in urine',
        ],
        'action': (
            'Schedule an appointment with your doctor within 24–48 hours. '
            'If symptoms worsen significantly, go to urgent care.'
        ),
        'contact': 'Primary Care Doctor',
    },
]

MENTAL_HEALTH_CRISIS_KEYWORDS = [
    'suicidal', 'suicide', 'self-harm', 'want to die', 'kill myself',
    'end my life', 'hopeless', 'no reason to live'
]


def detect_emergency(symptom_text: str) -> Dict:
    """
    Detect emergency severity from symptom text.
    Returns severity level, triggered keywords, and recommended action.
    """
    text_lower = symptom_text.lower()

    # Check mental health crisis first
    mental_health_triggers = [kw for kw in MENTAL_HEALTH_CRISIS_KEYWORDS if kw in text_lower]
    if mental_health_triggers:
        return {
            'severity': 'CRITICAL',
            'triggered_keywords': mental_health_triggers,
            'recommended_action': (
                'Please reach out for help immediately. '
                'Call or text 988 (Suicide & Crisis Lifeline). '
                'You are not alone - help is available 24/7.'
            ),
            'emergency_contact': '988',
        }

    # Check each severity level
    for rule in EMERGENCY_RULES:
        triggered = [kw for kw in rule['keywords'] if kw in text_lower]
        if triggered:
            return {
                'severity': rule['severity'],
                'triggered_keywords': triggered,
                'recommended_action': rule['action'],
                'emergency_contact': rule['contact'],
            }

    # Low severity - general monitoring
    return {
        'severity': 'LOW',
        'triggered_keywords': [],
        'recommended_action': (
            'Monitor your symptoms. Maintain good hydration and rest. '
            'If symptoms persist or worsen, consult a healthcare provider.'
        ),
        'emergency_contact': 'Primary Care Doctor',
    }
