"""Regenerate work/saves/: a game-written base save, then the edited ones derived from it with save.py.

    python -X utf8 tools/debug/make_saves.py [ROM]

1. runs the save_done scene (cold boot, overworld camp menu, save to FILE1) and keeps the .srm the game wrote as
   work/saves/base_file1.srm (slot 0 valid: magic and checksum checked by save.py);
2. writes the stress saves listed in STRESS (save.py edits of the base; each is loaded and asserted by
   tests or by the stress_* scenes in scenes.tsv).
Saves hold no ROM pointers, so they survive rebuilds; re-run after changing the save format or the base scene.
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))
from skill import SKILL  # noqa: E402
from save import Save  # noqa: E402

SAVES = ROOT / "work" / "saves"
# name -> (ram writes {addr: bytes}, room, x, y); room 77 = a house whose menus open at once (scenes menu_*)
STRESS = {
    "stress_money.srm": ({0x1DD1: (9999999).to_bytes(3, "little")}, 0x4D, 10, 6),
}


def main():
    rom = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "rom" / "Last Battle, The (Japan).sfc"
    out = ROOT / "work" / "qa" / "make_saves"
    if out.exists():
        shutil.rmtree(out)
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--script", str(ROOT / "tools" / "debug" / "warp.lua"), "--var", "SCENE='save_done'",
           "--frames", "4200", "--shot-every", "300", "--timeout", "600"]
    rc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).returncode
    srm = next(out.glob("*.srm"), None)
    if rc != 0 or srm is None:
        raise SystemExit(f"save_done run failed (exit {rc}, srm {srm}); see {out}")
    SAVES.mkdir(parents=True, exist_ok=True)
    data = srm.read_bytes()
    Save(data, 0)  # raises unless slot 0 holds a valid game-written save
    (SAVES / "base_file1.srm").write_bytes(data)
    print("base_file1.srm: game-written FILE1")
    for name, (writes, room, x, y) in STRESS.items():
        sv = Save(data, 0)
        for addr, bs in writes.items():
            for i, b in enumerate(bs):
                sv.set(addr + i, b)
        for addr, v in ((0xD24, room), (0xD26, x), (0xD28, y)):
            sv.set(addr, v & 0xFF)
            sv.set(addr + 1, v >> 8)
        b = sv.build()
        Save(b, 0)
        (SAVES / name).write_bytes(b)
        check_load(rom, SAVES / name, room, sv)
        print(f"{name}: room {room} ({x},{y}), {len(writes)} edits, loads in game: ok")


def check_load(rom, sav, room, sv):
    """Boot with the save, load FILE1 from the title and assert room and money in WRAM (save_check.lua)."""
    out = ROOT / "work" / "qa" / "make_saves" / sav.stem
    money = sv.ram[0x1DD1] | sv.ram[0x1DD2] << 8 | sv.ram[0x1DD3] << 16
    cmd = [sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "emu.py"), str(rom), "--out", str(out),
           "--sav", str(sav), "--route", str(ROOT / "tools" / "routes" / "load1.txt"), "--frames", "2600",
           "--shot-every", "600", "--timeout", "300", "--script", str(ROOT / "tools" / "debug" / "save_check.lua"),
           "--var", "AT=2500", "--var", f"ROOM={room}", "--var", f"MONEY={money}"]
    rc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT).returncode
    log = (out / "log.txt").read_text(encoding="utf-8", errors="replace") if (out / "log.txt").exists() else ""
    if rc != 0 or "SAVECHECK ok" not in log:
        raise SystemExit(f"{sav.name}: did not load as edited (exit {rc}); see {out}")


if __name__ == "__main__":
    main()
