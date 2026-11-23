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
- [ ] tactic_3 - `[FF]` kept between "Power" and "Attack" as in JP; confirm what the byte does on screen
- [ ] bt_19D4BB - real battle message (クルトに...), not a particle: translate once phase 7 solves its slot
- [ ] bg3_9EF0 - shop Buy left Japanese (4-byte slot, D11): translate when phase 7 repoints it, then `batches.py check b005`
- [ ] bg3_9EF8 - shop Sell left Japanese (4-byte slot, D11): translate when phase 7 repoints it
- [ ] bg3_A687 - feather note left Japanese (4-byte slot, D11): translate when phase 7 repoints it
- [ ] b050 - 11 untranslated entries in `work/tl/b050.tsv` (battle particles, equip-slot labels): translate in phase 7 and re-run `batches.py check b050`
