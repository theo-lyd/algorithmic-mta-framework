#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT_DIR/artifacts/phase-5/batch-5-3"
PKG_DIR="$OUT_DIR/model_package"

mkdir -p "$PKG_DIR"

cp "$ROOT_DIR/artifacts/phase-4/batch-4-2/markov_attribution_summary.json" "$PKG_DIR/"
cp "$ROOT_DIR/artifacts/phase-4/batch-4-3/propensity_model_summary.json" "$PKG_DIR/"
cp "$ROOT_DIR/artifacts/phase-4/batch-4-5/finance_bridge_summary.json" "$PKG_DIR/"

TAR_PATH="$OUT_DIR/model_package_v1.0.0.tar.gz"
tar -czf "$TAR_PATH" -C "$OUT_DIR" model_package

echo "Packaged artifacts at: $TAR_PATH"
