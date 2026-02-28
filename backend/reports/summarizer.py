import logging
from functools import lru_cache
import torch

logger = logging.getLogger('health_ai')


@lru_cache(maxsize=1)
def _get_model_bundle():
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from django.conf import settings

    model_name = settings.ML_MODELS.get('SUMMARIZER', 't5-small')
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    return tokenizer, model, device


def summarize(text: str, max_length: int = 150, min_length: int = 40) -> str:
    cleaned = ' '.join(text.split())
    if not cleaned:
        return ''

    try:
        tokenizer, model, device = _get_model_bundle()
        prompt = f'summarize: {cleaned[:4000]}'
        inputs = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
        inputs = {key: value.to(device) for key, value in inputs.items()}

        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_length=max_length,
                min_length=min_length,
                num_beams=4,
                early_stopping=True,
            )
        return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
    except Exception as exc:
        logger.warning('Transformer summarizer failed, using extractive fallback: %s', exc)
        sentences = cleaned.split('. ')
        return '. '.join(sentences[:3]).strip()
