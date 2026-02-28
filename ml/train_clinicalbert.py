"""
Fine-tune ClinicalBERT for symptom classification.

Usage:
  python train_clinicalbert.py \
      --data_path ./data/symptom_dataset.csv \
      --output_dir ./clinicalbert_model \
      --num_labels 9
"""

import argparse
import importlib
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

MODEL_NAME = 'emilyalsentzer/Bio_ClinicalBERT'


def compute_metrics(prediction_output):
    predictions = np.argmax(prediction_output.predictions, axis=1)
    return {
        'accuracy': accuracy_score(prediction_output.label_ids, predictions),
        'f1': f1_score(prediction_output.label_ids, predictions, average='weighted'),
    }


def main():
    datasets_module = importlib.import_module('datasets')
    transformers_module = importlib.import_module('transformers')
    DatasetDict = datasets_module.DatasetDict
    load_dataset = datasets_module.load_dataset
    AutoModelForSequenceClassification = transformers_module.AutoModelForSequenceClassification
    AutoTokenizer = transformers_module.AutoTokenizer
    Trainer = transformers_module.Trainer
    TrainingArguments = transformers_module.TrainingArguments

    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default='./data/symptom_dataset.csv')
    parser.add_argument('--output_dir', type=str, default='./clinicalbert_model')
    parser.add_argument('--num_labels', type=int, default=9)
    parser.add_argument('--epochs', type=int, default=3)
    parser.add_argument('--batch_size', type=int, default=16)
    parser.add_argument('--learning_rate', type=float, default=2e-5)
    args = parser.parse_args()

    dataset = load_dataset('csv', data_files=args.data_path)['train']

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(dataset['label'])
    dataset = dataset.add_column('labels', encoded_labels)

    train_indices, val_indices = train_test_split(
        list(range(len(dataset))),
        test_size=0.2,
        random_state=42,
        stratify=encoded_labels,
    )

    dataset_dict = DatasetDict({
        'train': dataset.select(train_indices),
        'validation': dataset.select(val_indices),
    })

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    def tokenize(batch):
        return tokenizer(batch['text'], padding='max_length', truncation=True, max_length=256)

    tokenized = dataset_dict.map(tokenize, batched=True)
    tokenized = tokenized.remove_columns(['text', 'label'])
    tokenized.set_format('torch')

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=min(args.num_labels, len(label_encoder.classes_)),
    )

    training_args = TrainingArguments(
        output_dir=args.output_dir,
        evaluation_strategy='epoch',
        save_strategy='epoch',
        learning_rate=args.learning_rate,
        per_device_train_batch_size=args.batch_size,
        per_device_eval_batch_size=args.batch_size,
        num_train_epochs=args.epochs,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model='f1',
        report_to='none',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized['train'],
        eval_dataset=tokenized['validation'],
        compute_metrics=compute_metrics,
    )

    trainer.train()
    trainer.save_model(args.output_dir)
    tokenizer.save_pretrained(args.output_dir)

    label_path = Path(args.output_dir) / 'label_classes.json'
    label_path.parent.mkdir(parents=True, exist_ok=True)
    label_path.write_text(json.dumps(list(label_encoder.classes_)), encoding='utf-8')

    metrics = trainer.evaluate()
    print('\nClinicalBERT Evaluation Metrics')
    print(f"Accuracy: {metrics.get('eval_accuracy', 0):.4f}")
    print(f"F1 Score: {metrics.get('eval_f1', 0):.4f}")

    if metrics.get('eval_accuracy', 0) >= 0.99:
        print(
            '\nWarning: Accuracy is near-perfect. This can happen with synthetic or repetitive datasets. '
            'Validate on external real-world samples before deployment.'
        )

    metrics_path = Path(args.output_dir) / 'evaluation_metrics.json'
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
