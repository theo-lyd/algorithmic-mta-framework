# Phase 0 Issues Log

Status: Active
Phase: 0
Last Updated: 2026-04-08

## Purpose
Record issues encountered in Phase 0 and how they were resolved.

## Issue 0.1 - Python dependency compatibility conflict
- What issue was encountered:
  - Reproducibility bootstrap hit a dependency conflict between pinned package versions.
- Cause:
  - Version incompatibility between pandas and Great Expectations constraints.
- Solution applied:
  - Adjusted pandas pin to a compatible version (`2.1.4`) aligned with the environment and validation scripts.
- How solution was implemented:
  - Updated dependency constraints and re-ran bootstrap + cold-start validation until both returned exit code 0.
- How to avoid in future:
  - Add dependency compatibility checks before freezing requirements for each phase batch.
  - Keep one compatibility matrix section in batch report for core packages.
- Lesson learned:
  - Reproducibility requires version-set validation, not only package pinning.

## Issue 0.2 - Local Git LFS hook false failures
- What issue was encountered:
  - Push attempts emitted LFS hook errors although repository did not use LFS-tracked files.
- Cause:
  - Residual local hooks in `.git/hooks` called `git-lfs` while `git-lfs` binary was absent.
- Solution applied:
  - Removed local LFS hook scripts and continued with normal Git flow.
- How solution was implemented:
  - Deleted `pre-push`, `post-commit`, `post-checkout`, and `post-merge` hook files that invoked `git-lfs`.
- How to avoid in future:
  - Validate repository LFS usage (`.gitattributes`) before enabling LFS hooks.
  - Keep local hooks minimal and repository-relevant.
- Lesson learned:
  - Local hook state can diverge from repository policy; validate both before troubleshooting push issues.

## Issue Template (for additional Phase 0 discoveries)
- What issue was encountered:
- Cause:
- Solution applied:
- How solution was implemented:
- How to avoid in future:
- Lesson learned:
