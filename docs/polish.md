# Polish (Minor findings)

One `- [ ] id - note` line per finding; the polish pass ticks each `[x]` (fixed, or `waived: reason`). The release
script refuses to run while any line is unticked. Sources: `docs/review-phase6.md` and the session-16 batch review.

- [ ] r192_1E31 - narration opens with `"` because the JP does (「クルトたちは...); check in game, drop the quote if it reads as speech
- [ ] r118_0B03 - book title "The Mystery of Miranchel" uses the armour spelling for ミランシェル; maybe the world (Ettmiranshel) is meant: check the book text
- [ ] bg3_A855 - description fragment "Ray" is terse to fit the D9 box; revisit if phase 7 widens the description window
- [ ] bg3_AA89 - description fragment "Rift" is terse to fit the D9 box; revisit if phase 7 widens the description window
- [ ] bg3_AB89 - description fragment "Go" is terse to fit the D9 box; revisit if phase 7 widens the description window
- [ ] spell_02 - spell name cut to 8 (D10): Mirror (Mirror Image); widen with the battle rows if phase 7 can
- [ ] spell_08 - spell name cut to 8 (D10): Mirror (Mirror Image)
- [ ] spell_07 - spell name cut to 8 (D10): Protect (Protection)
- [ ] spell_13 - spell name cut to 8 (D10): Protect (Protection)
- [ ] spell_10 - spell name cut to 8 (D10): Restore (Restore Health)
- [ ] spell_11 - spell name cut to 8 (D10): Thunder (Lightning)
- [ ] spell_14 - spell name cut to 8 (D10): Thunder (Lightning)
- [ ] spell_22 - spell name cut to 8 (D10): Awaken (Consciousness)
- [ ] spell_23 - spell name cut to 8 (D10): Seal Foe
- [ ] spell_24 - spell name cut to 8 (D10): MagicArm
- [ ] spell_27 - spell name cut to 8 (D10): Starfall (Star Blast)
- [x] tactic_3 - `[FF]` kept between "Power" and "Attack" as in JP; confirm what the byte does on screen (fixed phase 7: it printed as the text "[FF]"; now "All-Out", b061)
- [ ] bt_19D4BB - real battle message (クルトに...), not a particle: translate once seen in a battle (script/keep_jp.txt, phase 8)
- [x] bg3_9EF0 - shop Buy left Japanese (4-byte slot, D11): translate when phase 7 repoints it (fixed: window moved, D18, `work/qa/cap3/shopcmd.png`)
- [x] bg3_9EF8 - shop Sell left Japanese (4-byte slot, D11): translate when phase 7 repoints it (fixed with bg3_9EF0)
- [x] bg3_A687 - feather note left Japanese (4-byte slot, D11): translate when phase 7 repoints it (fixed: repointed, "Bird plume")
- [ ] bt_140017 - "defeated!!" / "s defeated!" glues a plural "s" onto the enemy name; check the rect width in game and rephrase if it allows
- [ ] bt_186247 - なにを？ rendered "??"; "What?" if the rect fits 5
- [ ] bt_1991EC - なにを？ rendered "What" with no question mark
- [ ] bt_19E144 - たいち rendered "Soil" while the mana is "Earth Mana" elsewhere; use "Earth" if 5 fits
- [ ] bt_1D8301 - ミス！ rendered "Nil"; "Miss" if 4 fits
- [ ] common_0384 - スヤスヤ rendered "Sleeping soundly...." reads as narration inside a quote; "Zzz... zzz...." fits the other sleepers
- [ ] cr_E2BD - composer 岡本 智郎 romanised "Tomoro"; confirm the reading (Tomoo / Tomorou) from an official credit
- [x] item_D3 - クロスオブマナ "Mana Cloth" vs item_3B "Mage's Cloth" and item_1E "Cloth of Law": one pattern for the "Cloth of X" family (fixed b061: Mana Robe / Mage Robe / Law Robe)
- [x] b050 - 11 untranslated entries in `work/tl/b050.tsv` (battle particles, equip-slot labels): translate in phase 7 and re-run `batches.py check b050` (equip labels done in phase 7; the 8 battle-only ones are in `script/keep_jp.txt` for phase 8)
- [ ] item_07 - 9-tile item names (D18) abbreviated where no natural 9-letter name exists: Sil.Sword, Sil.Mail (item_1C), Sil.Guard (item_28), Kn.Shield (item_25), SilvelYrn (item_C4), Drgn Tear (item_C9), Sil.Nepha / Lt. Nepha (item_E0/E1); revisit if a list ever gets wider
- [ ] bg3_A729 - equip-slot labels Wpn / Shld / Feet (2-tile slots repointed, D18): screen not identified yet; shoot it in phase 8 and widen the words if the window allows
- [ ] bg3_8F96 - status screen labels Atk / Def / Agi / Wis: the value op {009E} draws over anything past 5 letters (phase 7, `work/qa/p7/menu_status`); full words need the values moved
- [ ] menu_status - bottom-right window of the status screen shows a Japanese ま beside "Ma" (`work/qa/p7/menu_status/final.png`): graphics or an unextracted string, phase 8
- [ ] r085_0C94 - Ritten old man (r085_0C94..r085_11B0) and Gulva old man (r092_0127..r092_03EB): のぅ rendered as "eh" on nearly every sentence; vary the tag ("lad", "heh", dropped g's) so it reads less mechanical (b056 reworked r085_0D58/0DDA/0EDC)
- [ ] r118_0067 - library narration in present tense ("you find a grubby book") between past-tense captions; pick one tense for the library book captions
- [ ] top15_00E0 - secondhand-shop keeper ends with servile ハイ！ ("yessir!"); the EN drops it, the voice could carry it
- [ ] r009_005A - same JP as r319_0068: unify the wording (phase-6 review M1)
- [ ] r009_00D8 - same JP as r322_00A1 ("16" vs "sixteen", "had attacked" vs "attacked"): unify (M1)
- [ ] r009_0144 - same JP as r321_0074: unify (M1)
- [ ] r009_01C0 - same JP as r320_0059: unify (M1)
- [ ] r247_030F - same JP as r322_0106: unify (M1)
- [ ] r041_0F90 - same JP as r314_0192: unify (M1)
- [ ] r185_0580 - same JP as r313_01E0: unify (M1)
- [ ] r247_015A - same JP as r318_0121: unify (M1)
- [ ] r247_0212 - same JP as r318_01CD: unify (M1)
- [ ] r158_044F - healer line differs from r024_05DD/r065_0854: unify (M1)
- [ ] r074_00FB - "It's locked." vs "It is locked." x3: pick one (M1)
- [ ] b04_B65C - "There's nothing there." vs "There is nothing there." x10: pick one (M1)
- [ ] bg3_98B6 - same JP as bg3_89D2: unify (M1)
- [ ] r075_01FE - Guld captain's archaic ござる/つかまつる register rendered plain (session 18 re-read)
- [ ] top21_02FE, top23_0244, top23_03A4 - 合成 "combine" vs glossary 魔法合成 "spell synthesis": pick one wording with the menu label (session 18 re-read)
- [ ] shop buy list (FA3C): with 9-tile names the price ends one column right of the JP, so the sol sign is in the last
  inner column, touching the border (svc_00_13 "30000"); a 1-tile shift left of the price column would match the JP
  (session 23 visual QA)
- [ ] battle tactic box: "Basic" sits left in the 8-tile box the JP filled (ベーシックタイプ); the name rows are centred
  only by `insert.battle_rows` for the two-row form (battle_field, session 23)
- [ ] spell-cast box "Fireball / A": the rank letter alone on the bottom row; "Fireball A" fits 10 tiles, the box has
  8 (battle_room, session 23)
- [ ] field prompts with a character-name insert (`{FA0F} has no items.`) centre with the name at 8 tiles, so "Kurt"
  lines sit about a tile left (as the JP did with クルト); fine for 8-letter names (session 23)
- [ ] b04_C763 - dialogue {num} inserts print the old 12 px font digits ("Attack / 8 up", item Examine): taller than the VWF letters; check the other {num} lines (recovered {num} HP, {num} Sol) and draw the digits with the VWF if they all do this (session 27)
