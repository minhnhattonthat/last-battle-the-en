The Last Battle (SNES) - English translation patch v@VERSION@
===========================================================

Unofficial fan translation of "The Last Battle" (ザ・ラストバトル), Super Famicom, Teichiku 1994.
This zip holds only a patch and this file. No game data is included, and pre-patched ROMs are not
distributed: you need your own dump of the Japanese cartridge.

Base ROM (No-Intro: Last Battle, The (Japan).sfc)
  Size:   @SIZE@ bytes (no copier header)
  CRC32:  @CRC32@
  MD5:    @MD5@
  SHA-1:  @SHA1@

Patched ROM
  Size:   @PSIZE@ bytes (expanded to 4 MiB)
  CRC32:  @PCRC32@
  SHA-1:  @PSHA1@

How to patch
  1. Check that your dump matches the hashes above (a headered .smc must have its 512-byte header removed).
  2. Apply @PATCH@ with Flips, beat, or the web patcher at https://www.marcrobledo.com/RomPatcher.js/
  3. Play the patched .sfc in an accurate emulator. Tested in Mesen 2 (MesenCE).

Start from a cold boot: savestates made with the Japanese ROM or an earlier build carry old code and text.
In-game save files (SRAM) carry over.

Translation status
  Dialogue and story ............ translated
  Menus, items, spells, shops ... translated (item names fit 9 letters; a few are abbreviated)
  Battle text and windows ....... translated
  Title, logos, graphics text ... translated
  Name entry .................... English letters
  Staff credits ................. translated

Known issues
  - Item names are at most 9 letters and battle spell names 8, as the menu grids allow; a few are
    abbreviated (Sil.Sword, Kn.Shield, MagicArm...).
  - Item and spell description boxes are small fixed-tile boxes, so the descriptions are terse.
  Report bugs at https://github.com/minhnhattonthat/last-battle-the-en/issues (a savestate helps).

Credits
  Translation, hacking and tools: minhnhattonthat.
  Made with extensive AI assistance (Claude by Anthropic). Corrections are welcome.
  The Last Battle is (c) 1994 Teichiku. This project is not affiliated with Teichiku.
