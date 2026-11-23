# Skill gotchas (one line each: reference file it belongs in, then the fact)

- SKILL.md Step 0 / guard hook: in a fresh Orca worker session the plugin's guard did not block the canary; adding the `hooks` block with `python "$HOME/.claude/plugins/marketplaces/..."` worked (a `~` path inside quotes is not expanded and fails).
- emulator-qa.md: `emu.py --state-in` replays without the route/mash that made the state; a probe expecting the same events must pass the same `--mash` too (a WRAM dump without it showed the map never loaded).
- platform-snes.md / pipeline.md §Recon: `dis65816.py` is linear only; a flow-following walk that lists every access to the script pointer along all paths (this repo's `tools/re_flow.py`) gave each control code's argument layout, including byte-sized args and indirect sub-tables, in one pass. Candidate for the skill.
- pipeline.md §Recon (font ID): for a JIS-ordered kanji subset, a monotonic DP against rendered MS Gothic plus an eye proof (glyph over mapped char, 4-row strips: denser sheets were misread) found 42 aligner errors in 1066; checking the result is strictly JIS-increasing caught one off-by-one correction.
- SKILL.md / context-mode: Bash output over ~4 KB is replaced by an index stub; print compact summaries or Read files with offset/limit.
