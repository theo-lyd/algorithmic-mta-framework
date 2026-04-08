# Phase 2 Issues Log

Status: Active
Phase: 2
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 2 and how they were resolved.

## Issue Register
## Issue 2.1 - No blocking defect; deterministic policy hardening decision
- What issue was encountered:
	- No runtime failure occurred, but normalization policy could drift across systems without explicit deterministic rules.
- Cause:
	- Locale-sensitive text handling (umlauts, Eszett, whitespace) is often implemented inconsistently across tools.
- Solution applied:
	- Implemented explicit transliteration and join-key policy with fixture-locked tests.
- How solution was implemented:
	- Added `text_normalization.py`, fixture JSON, unittest coverage, and validation artifact generation.
- How to avoid in future:
	- Require fixture-based deterministic tests for all future normalization rules before promotion.
- Lesson learned:
	- Treat locale normalization as a data contract, not ad-hoc utility logic.

## Issue Template
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
