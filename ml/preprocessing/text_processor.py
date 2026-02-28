"""
ML preprocessing pipeline.
Text cleaning, normalization, and ICD code mapping utilities.
"""
import re
import logging
from typing import List, Dict

logger = logging.getLogger('health_ai')

# ICD-10 code mapping for common conditions
ICD_CODE_MAP = {
    'chest pain': 'R07.9',
    'shortness of breath': 'R06.00',
    'hypertension': 'I10',
    'type 2 diabetes': 'E11.9',
    'migraine': 'G43.909',
    'asthma': 'J45.909',
    'anxiety': 'F41.9',
    'depression': 'F32.9',
    'back pain': 'M54.5',
    'urinary tract infection': 'N39.0',
    'pneumonia': 'J18.9',
    'atrial fibrillation': 'I48.91',
    'heart failure': 'I50.9',
    'copd': 'J44.1',
    'osteoarthritis': 'M19.90',
    'hypothyroidism': 'E03.9',
    'anemia': 'D64.9',
    'gerd': 'K21.0',
    'stroke': 'I63.9',
    'seizure': 'R56.9',
}

# Common medical stopwords to remove
MEDICAL_STOPWORDS = {
    'i', 'me', 'my', 'have', 'has', 'had', 'been', 'am', 'is', 'are', 'was', 'were',
    'be', 'being', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might',
    'get', 'got', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
    'after', 'above', 'below', 'out', 'off', 'over', 'under', 'then', 'once',
}


def clean_medical_text(text: str) -> str:
    """
    Clean and normalize medical text.
    Steps: lowercase, remove special chars, normalize whitespace.
    """
    # Convert to lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove special characters (keep medical relevant punctuation)
    text = re.sub(r'[^\w\s\-/.]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str) -> List[str]:
    """Simple word tokenizer."""
    return clean_medical_text(text).split()


def remove_stopwords(tokens: List[str]) -> List[str]:
    """Remove medical stopwords from token list."""
    return [t for t in tokens if t not in MEDICAL_STOPWORDS and len(t) > 2]


def map_to_icd_codes(text: str) -> List[Dict]:
    """
    Map symptom text to ICD-10 codes.
    Returns list of {condition, icd_code} dicts.
    """
    text_lower = text.lower()
    mapped = []
    for condition, code in ICD_CODE_MAP.items():
        if condition in text_lower:
            mapped.append({'condition': condition, 'icd_code': code})
    return mapped


def preprocess_for_model(text: str, max_length: int = 256) -> str:
    """
    Full preprocessing pipeline for model input.
    """
    cleaned = clean_medical_text(text)
    tokens = tokenize(cleaned)
    # Truncate to max_length tokens
    if len(tokens) > max_length:
        tokens = tokens[:max_length]
    return ' '.join(tokens)


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for RAG processing.
    chunk_size: tokens per chunk
    overlap: token overlap between chunks
    """
    tokens = text.split()
    chunks = []
    start = 0
    while start < len(tokens):
        end = start + chunk_size
        chunk = ' '.join(tokens[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks
