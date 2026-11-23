# The Last Battle (SNES, Teichiku 1994) English translation

Skill: translate-retro-game (Claude Code: plugin, enabled in .claude/settings.json; other agents: `~/.claude/plugins/marketplaces/retro-translation/skills/translate-retro-game/SKILL.md`; `$SKILL` = the directory holding its SKILL.md, printed by `python tools/skill.py`). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    `python -X utf8 build.py`          -> build/lastbattle_en.sfc (checks the dump against `rom.sha1` first; exists from phase 3)
- Check:    `python -X utf8 tools/check.py`    (tests + lint; the pre-commit hook runs this; `git config core.hooksPath tools/hooks` once per clone)
- Smoke:    `python -X utf8 $SKILL/scripts/emu.py build/lastbattle_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Warp:     `python -X utf8 $SKILL/scripts/emu.py build/lastbattle_en.sfc --out work/qa/warp --script tools/debug/warp.lua --var "SCENE='<name>'" --frames 3000 --sheet` (scenes: `tools/debug/scenes.tsv`, RAM notes `docs/re/debug.md`; never ask the user to play to a scene). All scenes: `python -X utf8 tools/debug/run_scenes.py [ROM] [--only a,b] [--states]`; ad-hoc room/ops/pokes: `tools/debug/probe.py`
- Saves:    `python -X utf8 tools/debug/make_saves.py` (game-written FILE1 + stress saves in `work/saves/`, each loaded and asserted in game); edit one: `tools/debug/save.py dump|edit` (money, flags, room, any saved WRAM byte)
- Release:  `python -X utf8 tools/release.py` (patch + verify; never publish without the user)
- Clean:    `python -X utf8 tools/clean.py` (published projects: lists rebuildable/downloadable files; `--yes` deletes)

## Paths
- Original ROM: `rom/Last Battle, The (Japan).sfc` (gitignored; SHA-1 in `rom.sha1`, checked by `tools/check_rom.py`). Emulator: this repo's own MesenCE QA fork in `tools/mesen/` (release `qa-1`, https://github.com/minhnhattonthat/MesenCE/releases/download/qa-1/Mesen_qa-1_Windows.zip, via `$SKILL/scripts/fetch_emu.py mesen`; gitignored; settings in `tools/emu-config/`). Savestates: `work/states/`.
- Text: `script/` (JSON, one file per block). Tables: `tbl/`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`. Fonts and their licences: `docs/fonts.md`.
- Skill helpers copied in so a clone builds without the skill: `tools/tbl.py`, `tools/bps.py`, `tools/romdiff.py`. QA tools (`emu.py`, `qa_gate.py`, `jp_left.py`...) are called through `$SKILL`.

## Rulings
- Edit source files (.py .lua .asm .tbl .json) only with the file-edit tool; scripts here read and analyse, never `.replace()` and write back.
- Subagents: dispatch the agent types (translator, reviewer, visual-qa, playtester, graphics) shipped by the plugin as `translate-retro-game:<type>` (Claude Code), `.codex/agents/` (Codex) or `.opencode/agents/` (opencode), never general-purpose: their short tool list cuts each agent's start-up context from ~43k to ~9k tokens.
- The user's decisions, with the options and reasons: `docs/decisions.md`. Read it before asking the user anything; add each new ruling there the same session.
- Player bug reports: GitHub issues (`gh issue list --label bug`). Copy the attached save into `work/states/`, reproduce in the emulator, fix, commit with `Fixes #N`, and update `docs/status.md`.
- Gotchas: see `docs/re/README.md` and `docs/skill-gotchas.md`.

## Status
`docs/status.md`: done, next, open bugs. Update it at the end of every session.
