# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

All of D1-D8 came from the owner's standing answers injected into the Orca one-shot run (2026-11-23).

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-23 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing preference. |
| D2 | 2026-11-23 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist (e.g. manga/anime source), else an earlier fan patch, else Hepburn without macrons. |
| D3 | 2026-11-23 | Credits | stay Japanese, translate | English. |
| D4 | 2026-11-23 | Abbreviations | engine work first (default), abbreviate | Skill default: full names and terms, engine work before abbreviating. |
| D5 | 2026-11-23 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. The title logo is already English ("The Last Battle"). |
| D6 | 2026-11-23 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-23 | Existing saves / savestates | user saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-23 | Publishing | release zip, GitHub release | The run ends at a built and verified release zip; never `gh release create`, never change repo visibility. Commit and push to main at each phase end. |
| D9 | 2026-11-24 | Item and spell description boxes (6 x 7 and 7 x 4 fixed 8 px tiles; spell stat labels 4 tiles) | (a) write terse English to the measured boxes, abbreviating only where a word cannot fit (flagged in `glossary.md`); (b) engine work: draw the description through the dialogue VWF in a wide bottom box (36+ letters x 3 lines; the item menu has no bottom box, so a new window), a few sessions | **Agent default in the pre-approved run, not an owner ruling:** (a). BG3 has no free tiles for a narrower font and the neighbouring list windows fill the screen, so only (b) widens them; the Japanese is itself terse (4-5 kana per line) and 58 strings are cheap to rewrite if the owner picks (b). Listed under "Waiting on the user" (non-blocking). |
| D10 | 2026-11-24 | Item and tactic names (BG3 name fields 8 in the field item window, 9 in the shop list) | (a) abbreviate to 8 ("S.Sword"); (b) natural names up to 12 and widen the fields in phase 7 | **Agent default (pre-approved run): (b)**, per D4 (engine work before abbreviations). Names are 12 max (`tools/batches.py` NAME_CAP); phase 7 must widen `nm_icap`/the windows to 12 or a fit pass shortens the ~40 names over 9. Spells stay 8 (battle rows). |
| D11 | 2026-11-24 | BG3 menu labels whose window is the JP tile count (4-tile commands, 3-tile status words, 5-column stat headers) | (a) short words and standard RPG abbreviations now (Atk/Def/Agi/Wis/Lck, Psn/Par, Sys., Ster), revisit with window work; (b) block translation on window widening | **Agent default: (a)**, flagged here for the phase-7/8 window pass. Slots under 5 bytes can't relocate (shop Buy/Sell, one key-item note): left Japanese for phase 7 to repoint. |
