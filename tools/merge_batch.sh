#!/bin/sh
# Merge translated batch(es), build, run the full check, commit: sh tools/merge_batch.sh b016 [b017 ...]
# (docs/translator-brief.md step 4). Stops before the commit if the build or check fails.
set -e
cd "$(dirname "$0")/.."
python -X utf8 tools/batches.py merge "$@" | tail -1
python -X utf8 build.py | tail -1
python -X utf8 tools/check.py > work/check.log 2>&1 || { tail -20 work/check.log; exit 1; }
tail -1 work/check.log
git add script/ tools/batches.py glossary.md
git commit -qm "Phase 6: batch $*

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git log --oneline -1
