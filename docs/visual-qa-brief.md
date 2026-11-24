# Visual-QA reviewer brief - The Last Battle (SNES)

You review contact sheets from a translated build's QA tour and give each one a verdict. Read-only on everything
except your one verdict file: no edits to the repo, no git, no subagents.

## Inputs (in your dispatch)
- A chunk file: one `id<TAB>path` line per sheet. Read every sheet in it; none may be skipped.
- Your verdict file: `work/qa/verdicts/<chunk>.tsv`.
- Optional: the original ROM's sheets (`work/qa/tour_jp/`, same ids) and `glossary.md` (read it with offset/limit:
  whole-file reads above ~4 KB come back as a stub).

## How to look
- Read each sheet whole first. Where text is small, zoom into it with
  `python -X utf8 $SKILL/scripts/sheet.py SHEET.png --crop x,y,w,h --zoom 3 --out <scratch>.png` and read that.
- When something looks wrong, open the same id from `tour_jp/` (`sheet.py EN.png --compare JP.png`). If the
  original shows the same thing, it is the game's own behaviour: `ok`, with a note.
- Zoom into every Yes/No prompt, selection box, menu row and speech bubble: a few pixels of misalignment don't show
  at sheet scale. To measure one: `python -X utf8 $SKILL/scripts/inkbox.py SHOT.png x,y,w,h`.

## Judge
An `issue` is any of:
- Japanese still visible;
- text overflowing a box, clipped by a frame, or running off screen;
- text off-centre where the original centres it: an option in its selection box or cursor brackets, a label, a bubble;
- garbage tiles, wrong or missing glyphs, a strike or stray pixels across letters;
- broken line breaks: a word split mid-line, a page ending mid-sentence, a one-word last line;
- an empty box where text belongs;
- a name that differs from `glossary.md`.

Standing non-bugs, `ok` (the controller adds the game's own below):
- text still typing out, a box mid-fade or mid-scroll, a cursor caught mid-blink;
- a map or scene still loading after a warp;
- anything identical in the original's sheet.
- Menus use the game's fixed 8 px BG3 font (all caps look, `g`/`p` sit on the line): that is the font, not garbage.
  Since D19 its lowercase is bold (2 px stems) like the capitals; "OK"/"No", "Yes", "FILE1" in one style is right.
- Battle windows (messages, victory/EX/LEVEL UP windows, descriptions, command labels) draw English in proportional
  type from the same bold glyphs (D19, battle VWF); digits stay in fixed 8 px cells. Item and spell names in the
  battle lists (and the spell-cast window) stay in fixed cells by design. Still flag a mix of the two styles inside
  one message, clipped letters, or a gap that breaks a word.
- `KLT`/`RLT` on the portrait icons and the `YES`/`NO` icons are the original's own graphics (Latin in the JP too).
- Short item names are deliberate (D18: 9 tiles per list): `Drgn Tear`, `SilvelYrn`, `Sil.Sword`, `Kn.Shield`. Item
  info headers keep the long form (`Dragon Tear/`). Status labels `Atk Def Agi Wis Lck` are deliberate (D11). A
  9-tile name in the equipment window covers the small "E" equipped marker (the window has no 10th tile): waived.
- Item descriptions are 5 tiles per line (the item shop's panel) and hyphenate long words (`Fena-/mun`, `con-/fu-/
  sion`): deliberate. The typed battle messages (ambush, surprise attack, wipeout) reveal left to right while they
  type, then sit centred; "LEVEL UP!!" is one proportional run.
- Stray kana tiles at the right screen edge of `svc_0B_00`/`svc_0D_00` are leftover BG3 map from the room scroll.
- Speaker pages are `Name` on line 1, then the speech indented after a `"`; dialogue has no closing quote mark.
- Battle status-box names (`Kurt`, `Mei`, `Borg`, `Regina`) are a compact 4 px font with no descender on `g`: by design.
- Known and tracked (still mark them `issue` the first time, with a note "known"): battle particles in
  `script/keep_jp.txt`.

## Verdicts
Write your verdict file once you have read every sheet, one line per id in the chunk:
`id<TAB>ok|issue<TAB>what and where` (for an issue: which tile, which text, what is wrong).
Then return a short summary: counts, and the issues one per line.
