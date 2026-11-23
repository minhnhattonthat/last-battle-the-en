#!/bin/sh
# Battle text-coverage probes on the frozen coverage build (session-24 runs, redone after the textcover.lua fix):
# encounter @1DDF:0053 from room 0x00 at 40,30; commands menu up at ~f1100 (god mode), then each command path.
# Wipeout is the `wipeout` scene (cover_all.sh scenes). Output work/qa/cover/battle, log work/qa/cover_battle.log.
#   sh tools/debug/cover_battle.sh
cd "$(dirname "$0")/../.." || exit 1
[ -f work/qa/ranges.txt ] || python -X utf8 -c "import sys,pathlib;sys.path[:0]=['tools/debug','tools'];import textcover_run as t;print(t.rom_ranges(pathlib.Path('work/qa/cover_build/strings.tsv')))" > work/qa/ranges.txt
R="$(cat work/qa/ranges.txt),298000-29FFFF,A98000-A9FFFF"
P="0x00 40 30"
python -X utf8 tools/debug/probe.py work/qa/cover/battle --rom work/qa/cover_build/rom.sfc --frames 6000 --jobs 3 \
  --script tools/debug/textcover.lua --var "RANGES='$R'" \
  "$P 1100 -|-|god,@1DDF:0053" \
  "$P 300 -;6 a;14 -;6 a;14 -;6 a;14 -;6 a;14 -;6 a;14 -;6 a;14 -;6 a;14 -;6 a;14 -|-|god,win,@1DDF:0053" \
  "$P 300 -|-|@1DDF:0053" \
  "$P 1100 -;6 a;150 -;6 right;60 -;6 right;60 -;6 right;60 -;6 right;60 -|-|god,@1DDF:0053" \
  "$P 1100 -;6 a;150 -;6 a;120 -;6 a;120 -;6 down;30 -;6 a;120 -;6 a;200 -|-|god,@1DDF:0053" \
  "$P 1100 -;6 a;150 -;6 right;40 -;6 a;120 -;6 a;120 -;6 down;30 -;6 a;120 -;6 a;200 -|-|god,@1DDF:0053" \
  "$P 1100 -;6 a;150 -;6 right;40 -;6 a;120 -;6 down;30 -;6 down;30 -;6 a;120 -;6 a;120 -;6 b;60 -;6 b;60 -|-|god,@1DDF:0053" \
  "$P 1100 -;6 a;150 -;6 right;40 -;6 right;40 -;6 a;120 -;6 a;120 -;6 down;30 -;6 a;120 -;6 a;200 -|-|god,@1DDF:0053" \
  > work/qa/cover_battle.log 2>&1
echo BATTLE DONE >> work/qa/cover_battle.log
