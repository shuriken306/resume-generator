#!/usr/bin/env bash
# ──────────────────────────────────────────────
# Generate resume PDF with uv (no manual
# installation required)
#
# Usage:
#   ./generate.sh                          # defaults
#   ./generate.sh my_data.json             # custom JSON
#   ./generate.sh my_data.json out.pdf     # custom JSON + output
# ──────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA="${1:-${SCRIPT_DIR}/resume_data.json}"
OUTPUT="${2:-${SCRIPT_DIR}/resume.pdf}"

if [ ! -f "$DATA" ]; then
    echo "Error: $DATA not found."
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo "uv is not installed."
    echo "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv run --with reportlab "$SCRIPT_DIR/resume.py" "$DATA" --output "$OUTPUT"
