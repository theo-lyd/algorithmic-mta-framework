# Phase 3 Issues Log

Status: Active
Phase: 3
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 3 and how they were resolved.

## Issue Register
## Issue 3.1 - Historical attribution drift risk without point-in-time campaign joins
- What issue was encountered:
	- Campaign ownership, budget, and taxonomy can change over time, causing historical attribution drift if current-state attributes are joined.
- Cause:
	- Slowly changing campaign metadata is often overwritten in place by source systems.
- Solution applied:
	- Implemented SCD Type 2 windows and timestamp-based point-in-time joins.
- How solution was implemented:
	- Added `campaign_scd2.py`, deterministic change/event fixtures, replay tests, and validation summary artifact.
- How to avoid in future:
	- Enforce SCD2 + point-in-time join as mandatory contract for all historically variant dimensions.
- Lesson learned:
	- Attribution integrity depends on temporal correctness as much as raw event quality.

## Issue 3.2 - Ambiguous cross-identifier merges can corrupt customer profiles
- What issue was encountered:
	- A record with a new CRM id but already-linked email can silently merge into the wrong identity cluster.
- Cause:
	- Multi-identifier joins can expose conflicting clusters when CRM and web identifiers disagree.
- Solution applied:
	- Added explicit conflict detection and routed conflicts to unresolved identity queue.
- How solution was implemented:
	- Extended identity resolver with conflict rules, deterministic tests, and unresolved queue artifact output.
- How to avoid in future:
	- Treat cross-cluster identifier collisions as hard conflicts requiring manual triage, not auto-merge.
- Lesson learned:
	- Conservative unresolved-queue routing is safer than optimistic merge logic for identity integrity.

## Issue Template
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
