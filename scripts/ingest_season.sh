#!/usr/bin/env bash

set -euo pipefail

YEAR="${1:-2022}"
START_ROUND="${2:-5}"
END_ROUND="${3:-22}"
SESSION="${4:-race}"

for round_number in $(seq "$START_ROUND" "$END_ROUND"); do
    echo "Starting ${YEAR} round ${round_number} (${SESSION})"
    python -m src.ingestion.run \
        --year "$YEAR" \
        --round "$round_number" \
        --session "$SESSION"
done

echo "Ingestion completed: ${YEAR} rounds ${START_ROUND}-${END_ROUND} (${SESSION})"
