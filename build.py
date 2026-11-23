"""build.py: build build/lastbattle_en.sfc from the dump in rom/ (SHA-1 in rom.sha1, checked first).

Pipeline: unpack the LZ block region and its pointer tables (tools/blocks.py) -> splice script/*.json into the
blocks and raw text ranges (tools/insert.py; `en`, else `jp`) -> repack. Every write goes through put(), which refuses offsets outside tools/ranges.txt and logs
`OFFSET ORIG_HEX NEW_HEX writer` to build/writes.txt; romdiff.py then checks the output against the original with
that log (wrong original bytes, overlapping or overwritten writes, a changed byte no write explains).

With no edits the output is byte-identical to the original (tests/test_identity.py).

    python -X utf8 build.py [--out FILE] [--recompress]
--recompress runs every block through lz.compress (blocks move; the game must still run): a relocation check."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import battle_text  # noqa: E402
import blocks  # noqa: E402
import check_rom  # noqa: E402
import font_bg3  # noqa: E402
import font_en  # noqa: E402
import insert  # noqa: E402
import romdiff  # noqa: E402

ORIG_PATH = ROOT / "rom" / "Last Battle, The (Japan).sfc"
OUT = ROOT / "build" / "lastbattle_en.sfc"
ASAR = ROOT / "tools" / "asar" / "asar.exe"
ASM = ["vwf.asm"]
ROM_SIZE = 0x400000  # expanded to 4 MB: code, font and moved text go past 0x200000 ($C0:8000+)


def load_ranges(path=ROOT / "tools" / "ranges.txt"):
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        lo, _, hi = line.split()[0].partition("-")
        out.append((int(lo, 16), int(hi or lo, 16) + 1))
    return out


class Writer:
    """The one way to change the ROM: checks the range, logs the original bytes it replaces."""

    def __init__(self, orig, ranges):
        self.orig = orig
        self.rom = bytearray(orig)
        self.ranges = ranges
        self.log = []

    def put(self, off, data, by):
        end = off + len(data)
        if not any(lo <= off and end <= hi for lo, hi in self.ranges):
            raise ValueError(f"{by}: write 0x{off:06X}-0x{end - 1:06X} is outside tools/ranges.txt")
        if self.rom[off:end] == data:
            return
        old = self.orig[off:end].ljust(len(data), b"\xff")
        self.log.append((off, old, bytes(data), by))
        self.rom[off:end] = data


def apply_asm(w, asm_files=ASM):
    """Assemble asm/*.asm with asar onto a copy of w.rom and replay every changed run through w.put."""
    if not ASAR.exists():
        sys.exit(f"{ASAR} missing: unzip asar 1.91 from github.com/RPGHacker/asar/releases into tools/asar/")
    font_en.write(ROOT / "build")
    tmp = ROOT / "build" / "asar_tmp.sfc"
    tmp.write_bytes(w.rom)
    for asm in asm_files:
        r = subprocess.run([str(ASAR), "--fix-checksum=off", str(ROOT / "asm" / asm), str(tmp)],
                           capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"asar failed on {asm}:\n{r.stdout}{r.stderr}")
    new = tmp.read_bytes()
    tmp.unlink()
    assert len(new) == len(w.rom), "asar changed the image size"
    i, n = 0, len(new)
    while i < n:
        if new[i] == w.rom[i]:
            i += 1
            continue
        j = i
        while j < n and new[j:j + 8] != w.rom[j:j + 8]:  # runs closer than 8 bytes join
            j += 1
        w.put(i, new[i:j], "asm")
        i = j


def build(out=OUT, recompress=False, orig_path=ORIG_PATH, script_dir=insert.SCRIPT, asm=True, qa=None,
          marker=False, jp_only=False):
    """jp_only: ignore the English (identity tests: the script carries translations from phase 6 on)."""
    orig = orig_path.read_bytes()
    w = Writer(orig, load_ranges())
    region = blocks.unpack(orig)
    files = insert.load(script_dir)
    if jp_only:
        for doc in files.values():
            for e in doc["entries"]:
                e["en"] = ""
    if marker:
        insert.mark(files, insert.ruler_text if marker == "ruler" else insert.marker_text)
    insert.override(files, qa or {})
    if asm:
        w.rom.extend(b"\xff" * (ROM_SIZE - len(w.rom)))
        w.put(0x7FD7, b"\x0c", "header: 4 MB")
    insert.apply(orig, region, w, files, insert.TextAlloc() if asm else None)
    if asm:  # English lowercase in the 8x8 BG3 font (tools/font_bg3.py); the identity build leaves it alone
        b = region.blocks[font_bg3.BLOCK]
        b.data = font_bg3.patch(b.data)
        font_bg3.battle_patch(orig, w)
        battle_text.column_messages(orig, w)  # "Enemy ambush!!" / "Surprise attack!" (typed column by column)
    region.pack(w.rom, w.put, recompress=recompress, free=blocks.FREE + ([blocks.EXPANSION] if asm else []))
    if asm:
        apply_asm(w)
    rom = bytes(w.rom)
    errs, _ = romdiff.check(orig, rom, [], w.log)
    if errs:
        raise SystemExit("romdiff:\n" + "\n".join(errs))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(rom)
    lines = [f"{o:X} {a.hex()} {b.hex()} {by}" for o, a, b, by in w.log]
    out.with_name("writes.txt").write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8", newline="\n")
    return rom, w.log


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--recompress", action="store_true")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="QA build: replace one string's English (repeatable; build/ only, never script/)")
    ap.add_argument("--marker", action="store_true",
                    help="marker build: every string -> [id] + filler as wide as its Japanese line (default out "
                         "build/marker.sfc)")
    ap.add_argument("--ruler", action="store_true",
                    help="ruler build: every text line -> 40 digits of 6 px (the last digit seen = the box width / 6; "
                         "default out build/ruler.sfc); docs/re/windows.md")
    a = ap.parse_args()
    check_rom.check()
    qa = dict(s.split("=", 1) for s in a.qa)
    mode = "ruler" if a.ruler else a.marker
    out = ROOT / "build" / f"{'ruler' if a.ruler else 'marker'}.sfc" if mode and a.out == str(OUT) else a.out
    rom, log = build(out, a.recompress, qa=qa, marker=mode)
    import hashlib
    print(f"{out}: {len(rom)} bytes, {len(log)} writes, sha1 {hashlib.sha1(rom).hexdigest()}")


if __name__ == "__main__":
    main()
