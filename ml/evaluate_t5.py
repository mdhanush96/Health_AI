"""
Evaluate summarization quality using ROUGE.

Usage examples:
  python evaluate_t5.py \
      --model_name t5-small \
      --input_text "<real_report_text_here>" \
      --reference_summary "<gold_summary_here>"

  python evaluate_t5.py \
      --model_name t5-small \
      --input_file ./data/report_input.txt \
      --reference_file ./data/reference_summary.txt
"""

import argparse
from pathlib import Path

from rouge_score import rouge_scorer
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch


PLACEHOLDER_VALUES = {
    '<report_text>',
    '<reference_summary>',
    'report_text',
    'reference_summary',
}


def _load_text(value: str | None, file_path: str | None) -> str:
    if file_path:
        return Path(file_path).read_text(encoding='utf-8').strip()
    return (value or '').strip()


def _validate_input(name: str, value: str) -> None:
    normalized = value.strip().lower()
    if not normalized:
        raise ValueError(f'{name} is empty. Provide real clinical text.')
    if normalized in PLACEHOLDER_VALUES:
        raise ValueError(f'{name} is a placeholder ({value}). Provide real text instead.')
    if len(value.split()) < 25:
        raise ValueError(
            f'{name} is too short ({len(value.split())} words). Use realistic report text to evaluate summarization.'
        )


def _length_params(input_text: str) -> tuple[int, int]:
    word_count = len(input_text.split())
    max_length = min(150, max(30, int(word_count * 0.5)))
    min_length = min(max_length - 5, max(20, int(word_count * 0.2)))
    return max_length, min_length


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_name', type=str, default='t5-small')
    parser.add_argument('--input_text', type=str, default=None)
    parser.add_argument('--reference_summary', type=str, default=None)
    parser.add_argument('--input_file', type=str, default=None)
    parser.add_argument('--reference_file', type=str, default=None)
    args = parser.parse_args()

    input_text = _load_text(args.input_text, args.input_file)
    reference_summary = _load_text(args.reference_summary, args.reference_file)

    _validate_input('input_text', input_text)
    _validate_input('reference_summary', reference_summary)

    max_length, min_length = _length_params(input_text)

    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(args.model_name)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)

    prompt = f'summarize: {input_text}'
    encoded = tokenizer(prompt, return_tensors='pt', truncation=True, max_length=512)
    encoded = {key: value.to(device) for key, value in encoded.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **encoded,
            max_length=max_length,
            min_length=min_length,
            num_beams=4,
            early_stopping=True,
        )

    generated = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rougeL'], use_stemmer=True)
    scores = scorer.score(reference_summary, generated)

    print('Generated Summary:')
    print(generated)
    print('\nROUGE Metrics:')
    print(f"ROUGE-1 F1: {scores['rouge1'].fmeasure:.4f}")
    print(f"ROUGE-L F1: {scores['rougeL'].fmeasure:.4f}")


if __name__ == '__main__':
    main()
