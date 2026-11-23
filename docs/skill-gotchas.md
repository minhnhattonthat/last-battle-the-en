# Skill gotchas (one line each: reference file it belongs in, then the fact)

- SKILL.md Step 0 / guard hook: in a fresh Orca worker session the plugin's guard did not block the canary; adding the `hooks` block with `python "$HOME/.claude/plugins/marketplaces/..."` worked (a `~` path inside quotes is not expanded and fails).
- emulator-qa.md: `emu.py --state-in` replays without the route/mash that made the state; a probe expecting the same events must pass the same `--mash` too (a WRAM dump without it showed the map never loaded).
- SKILL.md / context-mode: Bash output over ~4 KB is replaced by an index stub; print compact summaries or Read files with offset/limit.
