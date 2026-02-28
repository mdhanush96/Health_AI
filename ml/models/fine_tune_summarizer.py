"""
Fine-tuning pipeline for T5/BART medical report summarization.

Usage:
    python fine_tune_summarizer.py \
        --dataset path/to/reports_dataset.csv \
        --output_dir ./models/t5_medical_summarizer \
        --epochs 5 \
        --batch_size 8 \
        --lr 3e-4

Dataset CSV format:
    report_text,summary
    "Full clinical report text...", "Short clinical summary..."
    ...

Evaluated using ROUGE-1, ROUGE-2, ROUGE-L metrics.
"""
import argparse
import logging
import os
import pandas as pd
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_summarizer(
    dataset_path: str,
    output_dir: str,
    model_name: str = 't5-small',
    epochs: int = 5,
    batch_size: int = 8,
    learning_rate: float = 3e-4,
    max_input_length: int = 512,
    max_target_length: int = 150,
):
    """Fine-tune T5 for medical report summarization."""
    try:
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM,
            Seq2SeqTrainingArguments,
            Seq2SeqTrainer,
            DataCollatorForSeq2Seq,
        )
        from torch.utils.data import Dataset
        from rouge_score import rouge_scorer
        import numpy as np
    except ImportError as e:
        logger.error(f'Required packages not installed: {e}')
        return

    df = pd.read_csv(dataset_path)
    assert 'report_text' in df.columns and 'summary' in df.columns, \
        "Dataset must have 'report_text' and 'summary' columns"

    train_df, val_df = train_test_split(df, test_size=0.2, random_state=42)
    logger.info(f'Train: {len(train_df)}, Val: {len(val_df)}')

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    class SummarizationDataset(Dataset):
        def __init__(self, texts, summaries):
            self.texts = list(texts)
            self.summaries = list(summaries)

        def __len__(self):
            return len(self.texts)

        def __getitem__(self, idx):
            inputs = tokenizer(
                self.texts[idx],
                max_length=max_input_length,
                truncation=True,
                padding='max_length',
                return_tensors='pt',
            )
            labels = tokenizer(
                self.summaries[idx],
                max_length=max_target_length,
                truncation=True,
                padding='max_length',
                return_tensors='pt',
            )
            return {
                'input_ids': inputs['input_ids'].squeeze(),
                'attention_mask': inputs['attention_mask'].squeeze(),
                'labels': labels['input_ids'].squeeze(),
            }

    train_dataset = SummarizationDataset(train_df['report_text'], train_df['summary'])
    val_dataset = SummarizationDataset(val_df['report_text'], val_df['summary'])

    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)

    def compute_metrics(eval_pred):
        predictions, labels = eval_pred
        decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
        labels = np.where(labels != -100, labels, tokenizer.pad_token_id)
        decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

        rouge1, rouge2, rougeL = [], [], []
        for pred, label in zip(decoded_preds, decoded_labels):
            scores = scorer.score(label, pred)
            rouge1.append(scores['rouge1'].fmeasure)
            rouge2.append(scores['rouge2'].fmeasure)
            rougeL.append(scores['rougeL'].fmeasure)

        return {
            'rouge1': np.mean(rouge1),
            'rouge2': np.mean(rouge2),
            'rougeL': np.mean(rougeL),
        }

    training_args = Seq2SeqTrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='rouge2',
        predict_with_generate=True,
        generation_max_length=max_target_length,
        fp16=torch.cuda.is_available(),
        logging_dir=os.path.join(output_dir, 'logs'),
        report_to='none',
    )

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
    )

    logger.info('Starting T5 summarization training...')
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    eval_results = trainer.evaluate()
    logger.info(f'ROUGE scores: {eval_results}')
    return eval_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fine-tune T5 for medical summarization')
    parser.add_argument('--dataset', required=True)
    parser.add_argument('--output_dir', default='./models/t5_medical_summarizer')
    parser.add_argument('--model_name', default='t5-small')
    parser.add_argument('--epochs', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=8)
    parser.add_argument('--lr', type=float, default=3e-4)
    args = parser.parse_args()

    train_summarizer(
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        model_name=args.model_name,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
