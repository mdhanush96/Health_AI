"""
Retrieval-Augmented Generation (RAG) system using FAISS + SBERT.
Provides grounded medical responses from a curated knowledge base.
"""
import json
import logging
import os
from typing import List, Dict

logger = logging.getLogger('health_ai')

# Sample medical knowledge base entries
SAMPLE_KNOWLEDGE_BASE = [
    {
        "id": "kb_001",
        "text": "Chest pain can indicate cardiac issues such as angina or myocardial infarction. Seek immediate medical attention if accompanied by shortness of breath, sweating, or radiating pain to the arm or jaw.",
        "category": "cardiovascular",
        "source": "Clinical Guidelines"
    },
    {
        "id": "kb_002",
        "text": "High blood pressure (hypertension) above 140/90 mmHg increases the risk of stroke and heart disease. Lifestyle modifications include reducing sodium intake, regular exercise, and stress management.",
        "category": "cardiovascular",
        "source": "AHA Guidelines"
    },
    {
        "id": "kb_003",
        "text": "Type 2 diabetes management involves blood glucose monitoring, HbA1c testing, dietary control, physical activity, and medication adherence. Regular ophthalmology and nephrology follow-ups are essential.",
        "category": "endocrine",
        "source": "ADA Guidelines"
    },
    {
        "id": "kb_004",
        "text": "Asthma is a chronic respiratory condition characterized by airway inflammation and bronchoconstriction. Treatment includes inhaled corticosteroids, bronchodilators, and allergen avoidance.",
        "category": "respiratory",
        "source": "GINA Guidelines"
    },
    {
        "id": "kb_005",
        "text": "Migraine headaches are characterized by severe unilateral throbbing pain, photophobia, and nausea. Triptans are first-line acute treatment. Preventive medications include topiramate and amitriptyline.",
        "category": "neurological",
        "source": "AAN Guidelines"
    },
    {
        "id": "kb_006",
        "text": "Fever above 38.3°C (101°F) may indicate infection. Common causes include viral upper respiratory infections, urinary tract infections, and pneumonia. Antipyretics like acetaminophen provide symptomatic relief.",
        "category": "infectious",
        "source": "CDC Guidelines"
    },
    {
        "id": "kb_007",
        "text": "Elevated LDL cholesterol above 130 mg/dL increases cardiovascular risk. Management includes dietary modifications (reducing saturated fats), regular exercise, and statin therapy if indicated.",
        "category": "cardiovascular",
        "source": "ACC/AHA Guidelines"
    },
    {
        "id": "kb_008",
        "text": "Depression is a mood disorder characterized by persistent sadness, loss of interest, sleep disturbances, and fatigue. Treatment includes CBT, antidepressants (SSRIs/SNRIs), and lifestyle modifications.",
        "category": "psychiatric",
        "source": "APA Guidelines"
    },
    {
        "id": "kb_009",
        "text": "Back pain is one of the most common musculoskeletal complaints. Most cases resolve with conservative management: rest, NSAIDs, physical therapy, and heat/cold therapy. Red flags include neurological deficits.",
        "category": "musculoskeletal",
        "source": "Clinical Guidelines"
    },
    {
        "id": "kb_010",
        "text": "GERD (acid reflux) presents with heartburn and regurgitation. Management includes dietary modifications (avoid trigger foods), elevating the head of the bed, and proton pump inhibitors (PPIs).",
        "category": "gastrointestinal",
        "source": "ACG Guidelines"
    },
]


class RAGSystem:
    """
    Retrieval-Augmented Generation system.
    Uses SBERT for semantic search over a medical knowledge base with FAISS indexing.
    """

    def __init__(self):
        self._index = None
        self._embedder = None
        self._knowledge_base: List[Dict] = []
        self._initialized = False

    def _initialize(self):
        if self._initialized:
            return

        self._load_knowledge_base()

        try:
            from sentence_transformers import SentenceTransformer
            import faiss
            import numpy as np
            from django.conf import settings

            model_name = settings.ML_MODELS.get('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            self._embedder = SentenceTransformer(model_name)

            # Build FAISS index
            texts = [item['text'] for item in self._knowledge_base]
            embeddings = self._embedder.encode(texts, convert_to_numpy=True)
            embeddings = embeddings.astype('float32')

            dim = embeddings.shape[1]
            self._index = faiss.IndexFlatL2(dim)
            self._index.add(embeddings)

            logger.info(f'FAISS index built with {len(texts)} documents')
        except Exception as e:
            logger.warning(f'FAISS/SBERT not available, using keyword search: {e}')

        self._initialized = True

    def _load_knowledge_base(self):
        """Load knowledge base from file or use defaults."""
        try:
            from django.conf import settings
            kb_path = settings.ML_MODELS.get('KNOWLEDGE_BASE_PATH', '')
            if kb_path and os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    self._knowledge_base = json.load(f)
                logger.info(f'Loaded {len(self._knowledge_base)} KB entries from {kb_path}')
                return
        except Exception as e:
            logger.warning(f'Could not load KB from file: {e}')
        self._knowledge_base = SAMPLE_KNOWLEDGE_BASE

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant documents for a query."""
        self._initialize()

        if self._index is not None and self._embedder is not None:
            try:
                return self._semantic_search(query, top_k)
            except Exception as e:
                logger.warning(f'Semantic search failed: {e}')

        return self._keyword_search(query, top_k)

    def _semantic_search(self, query: str, top_k: int) -> List[Dict]:
        """SBERT + FAISS semantic search."""
        import numpy as np
        query_embedding = self._embedder.encode([query], convert_to_numpy=True).astype('float32')
        distances, indices = self._index.search(query_embedding, min(top_k, len(self._knowledge_base)))
        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx < len(self._knowledge_base):
                doc = self._knowledge_base[idx].copy()
                doc['relevance_score'] = float(1 / (1 + dist))
                results.append(doc)
        return results

    def _keyword_search(self, query: str, top_k: int) -> List[Dict]:
        """Keyword-based fallback search."""
        query_words = set(query.lower().split())
        scored = []
        for doc in self._knowledge_base:
            doc_words = set(doc['text'].lower().split())
            score = len(query_words & doc_words) / max(len(query_words), 1)
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:top_k]]

    def generate_response(self, query: str, symptom_category: str = '') -> Dict:
        """Generate a grounded medical response using retrieved context."""
        retrieved_docs = self.retrieve(query, top_k=5)

        if not retrieved_docs:
            return {
                'response': 'Please consult a qualified healthcare professional for personalized medical advice.',
                'sources': [],
                'retrieved_context': '',
            }

        # Build context from retrieved documents
        context_parts = []
        for doc in retrieved_docs[:3]:
            context_parts.append(doc['text'])
        context = ' '.join(context_parts)

        # Try T5-based generation
        response_text = self._generate_with_model(query, context)

        return {
            'response': response_text,
            'sources': [d.get('source', 'Medical Guidelines') for d in retrieved_docs[:3]],
            'retrieved_context': context[:300],
        }

    def _get_generator(self):
        """Lazily load and cache the T5 generation pipeline."""
        if not hasattr(self, '_generator') or self._generator is None:
            try:
                from transformers import pipeline
                from django.conf import settings
                self._generator = pipeline(
                    'text2text-generation',
                    model=settings.ML_MODELS.get('SUMMARIZER', 't5-small'),
                )
            except Exception as e:
                logger.warning(f'T5 generator not available: {e}')
                self._generator = None
        return self._generator

    def _generate_with_model(self, query: str, context: str) -> str:
        """Generate response using T5 with retrieved context."""
        try:
            gen = self._get_generator()
            if gen is None:
                raise RuntimeError('Generator not available')
            prompt = f'Medical question: {query} Context: {context[:300]} Answer:'
            result = gen(prompt, max_length=150, truncation=True)
            return result[0]['generated_text']
        except Exception as e:
            logger.warning(f'RAG generation failed, using extractive response: {e}')
            # Return most relevant context sentence
            sentences = context.split('. ')
            return sentences[0] if sentences else context[:200]


_rag_instance = None


def get_rag_system() -> RAGSystem:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGSystem()
    return _rag_instance
