#!/bin/sh
# Run every block-key text-coverage probe on the frozen coverage build (work/qa/cover_build), 3 emulators at a time:
# field item use, every room (resumes: --skip-done), every scene. The ROM-key probes (names_cover.py items, itemdesc,
# examine, spells, spelldesc, sealdesc) are separate. Report:
#   python -X utf8 $SKILL/scripts/textcover.py work/qa/cover work/qa/cover_build/strings.tsv \
#     --waive docs/text_unshown.tsv --mask 0xFFFFFFFFFFFF
#   sh tools/debug/cover_all.sh      (from the repo root; logs work/qa/cover_*.log, "RERUN DONE" at the end)
cd "$(dirname "$0")/../.." || exit 1
python -X utf8 -c "import sys,pathlib;sys.path[:0]=['tools/debug','tools'];import textcover_run as t;print(t.rom_ranges(pathlib.Path('work/qa/cover_build/strings.tsv')))" > work/qa/ranges.txt
R="$(cat work/qa/ranges.txt),298000-29FFFF,A98000-A9FFFF"
[ -d work/qa/cover/use ] || python -X utf8 tools/debug/names_cover.py work/qa/cover/use use --frames 3600 > work/qa/cover_use.log 2>&1
python -X utf8 tools/debug/textcover_run.py work/qa/cover --rom work/qa/cover_build/rom.sfc \
  --strings work/qa/cover_build/strings.tsv --jobs 3 --skip-done > work/qa/cover_rooms3.log 2>&1
python -X utf8 tools/debug/run_scenes.py work/qa/cover_build/rom.sfc --out work/qa/cover/scenes --jobs 3 \
  --script tools/debug/textcover.lua --var "RANGES='$R'" > work/qa/cover_scenes3.log 2>&1
echo RERUN DONE >> work/qa/cover_rooms3.log
