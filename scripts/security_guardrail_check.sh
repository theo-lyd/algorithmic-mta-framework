#!/usr/bin/env bash
set -euo pipefail

OUT_FILE="doc/phase-0/batch-0-3-security-validation.md"
mkdir -p doc/phase-0

# Patterns intentionally broad to catch accidental secret-like tokens.
PATTERN='(AKIA[0-9A-Z]{16}|-----BEGIN (RSA|OPENSSH|EC|DSA)? ?PRIVATE KEY-----|api[_-]?key\s*[:=]|secret\s*[:=]|password\s*[:=])'

HITS=$(grep -RInE --exclude-dir=.git --exclude-dir=.venv --exclude='*.md' --exclude='*.txt' "$PATTERN" . || true)

{
  echo "# Batch 0.3 Security Validation"
  echo
  echo "Date: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo
  echo "## Checks"
  echo "- .env ignored in .gitignore"
  if grep -q '^\.env$' .gitignore; then
    echo "PASS: .env is ignored"
  else
    echo "FAIL: .env is not ignored"
    exit 1
  fi
  echo
  echo "- Scan repository for common secret patterns (excluding markdown/text)"
  if [[ -n "$HITS" ]]; then
    echo "FAIL: Potential secret-like patterns detected"
    echo
    echo "### Findings"
    echo '```'
    echo "$HITS"
    echo '```'
    exit 1
  else
    echo "PASS: No potential secret-like patterns detected"
  fi
  echo
  echo "- Policy docs present"
  for f in \
    doc/phase-0/secrets-key-rotation.md \
    doc/phase-0/pii-classification-masking.md \
    doc/phase-0/access-control-matrix.md; do
    if [[ -f "$f" ]]; then
      echo "PASS: $f"
    else
      echo "FAIL: missing $f"
      exit 1
    fi
  done
} > "$OUT_FILE"

echo "Security validation artifact generated at $OUT_FILE"
