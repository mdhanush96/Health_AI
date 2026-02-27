"""
Fine-tuning pipeline for ClinicalBERT symptom classification.

Usage:
    python fine_tune_classifier.py \
        --dataset path/to/symptom_dataset.csv \
        --output_dir ./models/clinical_bert_classifier \
        --epochs 3 \
        --batch_size 16 \
        --lr 2e-5

Dataset CSV format:
    text,label
    "patient presents with chest pain",cardiovascular
    "shortness of breath on exertion",respiratory
    ...
"""
import argparse
import logging
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score, classification_report

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LABEL_CATEGORIES = [
    'cardiovascular', 'respiratory', 'neurological', 'gastrointestinal',
    'musculoskeletal', 'endocrine', 'dermatological', 'infectious', 'psychiatric',
]


def train_classifier(
    dataset_path: str,
    output_dir: str,
    model_name: str = 'emilyalsentzer/Bio_ClinicalBERT',
    epochs: int = 3,
    batch_size: int = 16,
    learning_rate: float = 2e-5,
    max_length: int = 256,
    test_size: float = 0.2,
):
    """Train ClinicalBERT for symptom classification."""
    try:
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSequenceClassification,
            TrainingArguments,
            Trainer,
        )
        from torch.utils.data import Dataset
    except ImportError as e:
        logger.error(f'Required packages not installed: {e}')
        return

    # Load dataset
    logger.info(f'Loading dataset from {dataset_path}')
    df = pd.read_csv(dataset_path)
    assert 'text' in df.columns and 'label' in df.columns, "Dataset must have 'text' and 'label' columns"

    # Encode labels
    le = LabelEncoder()
    df['label_id'] = le.fit_transform(df['label'])
    num_labels = len(le.classes_)
    logger.info(f'Found {num_labels} classes: {list(le.classes_)}')

    # Split
    train_df, val_df = train_test_split(df, test_size=test_size, random_state=42, stratify=df['label_id'])
    logger.info(f'Train: {len(train_df)}, Val: {len(val_df)}')

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    class SymptomDataset(Dataset):
        def __init__(self, texts, labels):
            self.encodings = tokenizer(
                list(texts),
                truncation=True,
                padding=True,
                max_length=max_length,
                return_tensors='pt',
            )
            self.labels = torch.tensor(list(labels), dtype=torch.long)

        def __getitem__(self, idx):
            item = {key: val[idx] for key, val in self.encodings.items()}
            item['labels'] = self.labels[idx]
            return item

        def __len__(self):
            return len(self.labels)

    train_dataset = SymptomDataset(train_df['text'], train_df['label_id'])
    val_dataset = SymptomDataset(val_df['text'], val_df['label_id'])

    # Load model
    model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels)

    def compute_metrics(eval_pred):
        logits, labels = eval_pred
        preds = np.argmax(logits, axis=-1)
        return {
            'accuracy': accuracy_score(labels, preds),
            'f1_macro': f1_score(labels, preds, average='macro'),
        }

    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=learning_rate,
        weight_decay=0.01,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        load_best_model_at_end=True,
        metric_for_best_model='f1_macro',
        fp16=torch.cuda.is_available(),
        logging_dir=os.path.join(output_dir, 'logs'),
        logging_steps=50,
        report_to='none',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics,
    )

    logger.info('Starting training...')
    trainer.train()

    # Save model and tokenizer
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Save label encoder
    import json
    with open(os.path.join(output_dir, 'label_classes.json'), 'w') as f:
        json.dump(list(le.classes_), f)

    logger.info(f'Model saved to {output_dir}')

    # Final evaluation
    eval_results = trainer.evaluate()
    logger.info(f'Final evaluation: {eval_results}')
    return eval_results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fine-tune ClinicalBERT for symptom classification')
    parser.add_argument('--dataset', required=True, help='Path to CSV dataset')
    parser.add_argument('--output_dir', default='./models/clinical_bert_classifier')
    parser.add_argument('--model_name', default='emilyalsentzer/Bio_ClinicalBERT')
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--lr', type=float, default=2e-5)
    parser.add_argument('--max_length', type=int, default=256)
    args = parser.parse_args()

    train_classifier(
        dataset_path=args.dataset,
        output_dir=args.output_dir,
        model_name=args.model_name,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        max_length=args.max_length,
    )
