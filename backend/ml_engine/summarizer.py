"""
Medical Report Summarizer using T5/BART.
"""
import logging

logger = logging.getLogger('health_ai')

# Medical abbreviation normalization map
MEDICAL_ABBREVIATIONS = {
    'bp': 'blood pressure',
    'hr': 'heart rate',
    'rr': 'respiratory rate',
    'temp': 'temperature',
    'wbc': 'white blood cell count',
    'rbc': 'red blood cell count',
    'hgb': 'hemoglobin',
    'hct': 'hematocrit',
    'plt': 'platelets',
    'bun': 'blood urea nitrogen',
    'cr': 'creatinine',
    'na': 'sodium',
    'k': 'potassium',
    'cl': 'chloride',
    'co2': 'carbon dioxide',
    'glucose': 'blood glucose',
    'ldl': 'low-density lipoprotein cholesterol',
    'hdl': 'high-density lipoprotein cholesterol',
    'tg': 'triglycerides',
    'ekg': 'electrocardiogram',
    'ecg': 'electrocardiogram',
    'mri': 'magnetic resonance imaging',
    'ct': 'computed tomography',
    'cbc': 'complete blood count',
    'bmp': 'basic metabolic panel',
    'cmp': 'comprehensive metabolic panel',
    'uri': 'upper respiratory infection',
    'uti': 'urinary tract infection',
    'dm': 'diabetes mellitus',
    'htn': 'hypertension',
    'cad': 'coronary artery disease',
    'chf': 'congestive heart failure',
    'copd': 'chronic obstructive pulmonary disease',
    'gerd': 'gastroesophageal reflux disease',
    'pvd': 'peripheral vascular disease',
    'afib': 'atrial fibrillation',
    'mi': 'myocardial infarction',
    'dvt': 'deep vein thrombosis',
    'pe': 'pulmonary embolism',
    'tia': 'transient ischemic attack',
    'cvd': 'cardiovascular disease',
}


def normalize_medical_text(text: str) -> str:
    """Normalize medical abbreviations and clean text."""
    import re
    # Lowercase
    text = text.lower()
    # Replace common abbreviations
    for abbr, full in MEDICAL_ABBREVIATIONS.items():
        text = re.sub(r'\b' + re.escape(abbr) + r'\b', full, text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class ReportSummarizer:
    """
    Medical report summarizer using T5-small / BART.
    Falls back to extractive summarization if models are unavailable.
    """

    def __init__(self):
        self._pipeline = None
        self._pipeline_loaded = False

    def _load_pipeline(self):
        if self._pipeline_loaded:
            return
        try:
            from transformers import pipeline
            from django.conf import settings
            model_name = settings.ML_MODELS.get('SUMMARIZER', 't5-small')
            self._pipeline = pipeline(
                'summarization',
                model=model_name,
                max_length=150,
                min_length=40,
                do_sample=False,
            )
            logger.info(f'Summarization pipeline loaded: {model_name}')
        except Exception as e:
            logger.warning(f'Summarization model not available: {e}')
        self._pipeline_loaded = True

    def summarize(self, text: str, max_input_length: int = 512) -> str:
        """Summarize medical report text."""
        self._load_pipeline()

        # Normalize and truncate
        cleaned = normalize_medical_text(text)
        words = cleaned.split()
        if len(words) > max_input_length:
            cleaned = ' '.join(words[:max_input_length])

        if self._pipeline is not None:
            try:
                result = self._pipeline(cleaned, truncation=True)
                return result[0]['summary_text']
            except Exception as e:
                logger.warning(f'Model summarization failed: {e}')

        # Fallback: extractive summarization (first 3 sentences)
        return self._extractive_summary(cleaned)

    def _extractive_summary(self, text: str, num_sentences: int = 3) -> str:
        """Simple extractive summary - return first N sentences."""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        # Filter meaningful sentences
        sentences = [s for s in sentences if len(s.split()) >= 5]
        summary = ' '.join(sentences[:num_sentences])
        return summary if summary else text[:300]


_summarizer_instance = None


def get_summarizer() -> ReportSummarizer:
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = ReportSummarizer()
    return _summarizer_instance
