# Graphics-text survey (phase 1, in progress)

Every screen with Japanese (or English that needs no change) drawn as tiles rather than through the text engine.
Columns: screen, how reached, layer, first guess at the source.

| Screen | Reached | Layer | Japanese? | Source guess |
|---|---|---|---|---|
| Teichiku logo | boot f300 | BG | English already | - |
| Title logo "The Last Battle", PUSH START / NEWGAME, ©1994 TEICHIKU | boot f600-900 | BG/sprites | English already (D5: keep logo) | - |
| Name entry: kana grid (アイウエオ / あいうえお ... arrows, `E_D` end key) | boot route + A | BG3 window | yes | probably tile codes `< $0300` or text-engine strings; check in phase 4 |
| Name entry: second screen shows "SAT ADA..." in Latin | `work/qa/play1` f1600 | BG3 | mixed | text engine |
| In-room dialogue window | `work/qa/play1` f2000+ | BG3 bitmap canvas | yes (text engine) | not graphics |

Still to survey (needs the phase-2 debug tool to reach them): field menu, status, items, equipment, shops,
battle screen (commands, messages), save/load, game over, chapter cards, ending, credits. Then the static sweep:
`tiles.py render` over every raw region and every decompressed block (`tools/re_blocks.py`), read in chunks.
