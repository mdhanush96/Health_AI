import re
from typing import Dict, List

from .clinical_data_store import get_clinical_data_store
from .rag import get_rag_system


class RAGPipeline:
    def __init__(self):
        self._rag_system = get_rag_system()
        self._store = get_clinical_data_store()

    def generate_educational_explanation(self, query: str, condition: str) -> str:
        retrieved_docs = self._rag_system.retrieve(query, top_k=4)
        if not retrieved_docs:
            return (
                f"Educational context for {condition}: monitor symptom progression and seek professional care "
                "if symptoms worsen or new red flags appear."
            )

        context_parts: List[str] = [doc.get('text', '') for doc in retrieved_docs[:3]]
        context = ' '.join(context_parts)

        text = (
            f"Educational explanation for {condition}: {context} "
            "Preventive awareness: maintain follow-up, monitor warning signs, and seek urgent care for red-flag symptoms."
        )
        return self._sanitize_for_safety(text)

    def _sanitize_for_safety(self, text: str) -> str:
        safe_text = text

        # LLM must never generate medications
        # All medication data must come from structured dataset
        for med in self._store.medication_safety:
            med_name = med.get('name', '').strip()
            if med_name:
                pattern = re.compile(rf'\b{re.escape(med_name.replace("_", " "))}\b', re.IGNORECASE)
                safe_text = pattern.sub('structured medication guidance', safe_text)

        safe_text = re.sub(r'\b\d+\s?(mg|mcg|g|ml|units)\b', '', safe_text, flags=re.IGNORECASE)
        safe_text = re.sub(r'\s{2,}', ' ', safe_text).strip()
        return safe_text


_RAG_PIPELINE = None


def get_rag_pipeline() -> RAGPipeline:
    global _RAG_PIPELINE
    if _RAG_PIPELINE is None:
        _RAG_PIPELINE = RAGPipeline()
    return _RAG_PIPELINE
