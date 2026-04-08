# Batch 4.4 Behavioral Segmentation Validation

Date: 2026-04-08

## Scope
Validate segmentation pipeline:
1. RFM and engagement feature engineering.
2. K-means clustering with silhouette/stability checks.
3. Segment labels and action playbooks.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_behavioral_segmentation.py
```

## Results
- Selected k: 2
- Silhouette score: 0.4419
- Stability score (mean ARI): 1.0
- Segment labels generated: Champions, Loyal

## Evidence Artifacts
- `artifacts/phase-4/batch-4-4/behavioral_segmentation_summary.json`
- `artifacts/phase-4/batch-4-4/segment_labels.csv`
