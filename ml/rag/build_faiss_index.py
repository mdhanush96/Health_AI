"""
FAISS index builder for RAG system.

Usage:
    python build_faiss_index.py \
        --knowledge_base path/to/knowledge_base.json \
        --output_dir ./ml_data \
        --model all-MiniLM-L6-v2

Knowledge base JSON format:
    [
        {"id": "doc_001", "text": "Medical text...", "category": "cardiovascular", "source": "Guidelines"},
        ...
    ]
"""
import argparse
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_index(
    knowledge_base_path: str,
    output_dir: str,
    model_name: str = 'all-MiniLM-L6-v2',
    chunk_size: int = 300,
    chunk_overlap: int = 50,
):
    """Build FAISS index from knowledge base documents."""
    try:
        import faiss
        import numpy as np
        from sentence_transformers import SentenceTransformer
    except ImportError as e:
        logger.error(f'Required packages not installed: {e}')
        return

    # Load knowledge base
    with open(knowledge_base_path, 'r') as f:
        documents = json.load(f)
    logger.info(f'Loaded {len(documents)} documents')

    # Load SBERT model
    logger.info(f'Loading embedding model: {model_name}')
    embedder = SentenceTransformer(model_name)

    # Chunk documents if needed
    chunked_docs = []
    for doc in documents:
        text = doc['text']
        words = text.split()
        if len(words) <= chunk_size:
            chunked_docs.append(doc)
        else:
            # Split into chunks
            start = 0
            chunk_idx = 0
            while start < len(words):
                end = start + chunk_size
                chunk_text = ' '.join(words[start:end])
                chunked_docs.append({
                    **doc,
                    'id': f"{doc['id']}_chunk_{chunk_idx}",
                    'text': chunk_text,
                })
                chunk_idx += 1
                start += chunk_size - chunk_overlap

    logger.info(f'Total chunks: {len(chunked_docs)}')

    # Generate embeddings
    texts = [doc['text'] for doc in chunked_docs]
    logger.info('Generating embeddings...')
    embeddings = embedder.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    embeddings = embeddings.astype('float32')

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    logger.info(f'FAISS index built: {index.ntotal} vectors, dim={dim}')

    # Save index and metadata
    os.makedirs(output_dir, exist_ok=True)
    faiss_path = os.path.join(output_dir, 'faiss_index.bin')
    metadata_path = os.path.join(output_dir, 'faiss_metadata.json')

    faiss.write_index(index, faiss_path)
    with open(metadata_path, 'w') as f:
        json.dump(chunked_docs, f, indent=2)

    logger.info(f'Saved FAISS index to {faiss_path}')
    logger.info(f'Saved metadata to {metadata_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build FAISS index for RAG')
    parser.add_argument('--knowledge_base', required=True)
    parser.add_argument('--output_dir', default='./ml_data')
    parser.add_argument('--model', default='all-MiniLM-L6-v2')
    parser.add_argument('--chunk_size', type=int, default=300)
    parser.add_argument('--chunk_overlap', type=int, default=50)
    args = parser.parse_args()

    build_index(
        knowledge_base_path=args.knowledge_base,
        output_dir=args.output_dir,
        model_name=args.model,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
