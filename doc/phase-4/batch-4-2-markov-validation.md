# Batch 4.2 Markov Attribution Validation

Date: 2026-04-08

## Scope
Validate Markov chain attribution controls:
1. Transition matrix from observed journey paths.
2. Channel removal-effect computation.
3. Attribution normalization to 100 percent share.

## Validation Command
```bash
PYTHONPATH=. python ingestion/pipeline/validate_markov_attribution.py
```

## Results
- Total conversions: 4
- Channels scored: 5
- Attribution share sum: 1.0
- Max channel share: 0.2761
- Min channel share: 0.1104

## Evidence Artifact
- `artifacts/phase-4/batch-4-2/markov_attribution_summary.json`
