# The Last Battle English translation

Unofficial English fan translation of **The Last Battle** (ザ・ラストバトル; Super Famicom, Teichiku, 1994): the
source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story | Translated |
| Menus, items, spells, shops, system messages | Translated (item names fit 9 letters, battle spell names 8; a few abbreviated) |
| Battle text and windows | Translated |
| Title screen, logos, graphics with text | Translated |
| Name entry | English letters |
| Staff credits | Translated |

Known issues: item and spell description boxes are small fixed-tile boxes, so descriptions are terse; see
[Issues](../../issues) for anything else.

Tested in Mesen 2 (this repo's MesenCE build). Start from a cold boot: savestates from the Japanese ROM or an older
build carry old code and text.

## Base ROM

| | |
|---|---|
| File (No-Intro) | `Last Battle, The (Japan).sfc` (no copier header) |
| Size | 2097152 bytes |
| CRC32 | `200EC9C8` |
| MD5 | `3c9f29d6e1c457156005f90bd9ea2b10` |
| SHA-1 | `2474c7aa8451d51784a3b852b9806495b4147cfb` |

The patched ROM is expanded to 4 MiB; its hashes are in the release README.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | pytest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/last-battle-the-en
cd last-battle-the-en
# copy your dump to: rom/Last Battle, The (Japan).sfc
#   (2097152 bytes, SHA-1 2474c7aa8451d51784a3b852b9806495b4147cfb; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/lastbattle_en.sfc
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Teichiku's and is included only so
the translation can be checked against it. The Last Battle is (c) 1994 Teichiku; this project is not affiliated with
them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic). Corrections are very welcome.
