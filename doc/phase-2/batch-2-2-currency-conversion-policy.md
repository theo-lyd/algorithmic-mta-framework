# Batch 2.2 Currency Conversion Policy (Effective-Date)

## Purpose
Define deterministic normalization of non-EUR amounts into EUR using effective-date exchange rates.

## Policy Rules
1. Currency detection priority:
- Explicit currency code/symbol in the raw text.
- Optional upstream currency hint when text is ambiguous.
- Default to EUR if no currency indicator exists.

2. Effective-date rate selection:
- For each currency, use the latest configured FX rate where `effective_date >= rate_start_date`.
- If no matching rate exists for the date, fail fast with explicit error.

3. Supported currencies in Batch 2.2:
- EUR
- USD
- GBP
- CHF

4. Magnitude and locale parsing:
- Parse abbreviations (`Mio`, `Mrd`, `million`, `billion`).
- Normalize decimal and thousands separators before conversion.

## Deterministic Rate Schedule (Current)
| Currency | Start Date | EUR Rate |
|---|---|---|
| USD | 2026-01-01 | 0.92 |
| USD | 2026-04-01 | 0.90 |
| GBP | 2026-01-01 | 1.18 |
| GBP | 2026-04-01 | 1.16 |
| CHF | 2026-01-01 | 1.03 |
| CHF | 2026-04-01 | 1.02 |
| EUR | 1900-01-01 | 1.00 |

## Implementation Reference
- `ingestion/pipeline/financial_normalization.py`

## Future Policy Controls
- Move rates to managed source table with versioning and governance approval workflow.
- Add rate-source metadata and integrity checks in Phase 4 quality contracts.
