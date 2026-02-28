# Model Evaluation Report

## ClinicalBERT (Symptom Classification)

Run command:

```bash
cd ml
python train_clinicalbert.py --data_path ./data/symptom_dataset.csv --output_dir ./clinicalbert_model
```

Fill after run:

| Metric | Value |
|--------|-------|
| Accuracy | 1.0000 (current synthetic split run) |
| F1 Score (weighted) | 1.0000 (current synthetic split run) |

Note: Near-perfect scores usually indicate synthetic/repetitive patterns or train-validation leakage risk. Validate on external clinical samples before final claims.


## T5 (Report Summarization)

Run command:

```bash
cd ml
python evaluate_t5.py \
  --model_name t5-small \
  --input_text "<report_text>" \
  --reference_summary "<gold_summary>"
```

Fill after run:

| Metric | Value |
|--------|-------|
| ROUGE-1 F1 | 0.1978 |
| ROUGE-L F1 | 0.1538 |

