"""insert.py: write script/*.json back into the ROM image during build.py (docs/re/text.md).

Each entry's text is `en` when set, else `jp`, encoded and spliced back at its address: script blocks into the
block's decompressed data (blocks.Region repacks and recompresses only changed blocks), raw banks and byte names
through Writer.put. With no English every write reproduces the original bytes (tests/test_identity.py).

A string never changes size in place (block images and bank 04 keep every address, so no pointer moves): a longer one
is written to TEXT_AREA and its slot becomes a far jump there, the moved copy ending in a far jump back to the byte
after the slot; a shorter one is padded with spaces or followed by a far jump over the rest (docs/re/vwf.md §Far)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from textcodec import EN, JP, ByteCodec  # noqa: E402

SCRIPT = ROOT / "script"


def load(script_dir=SCRIPT):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(script_dir).glob("*.json"))}


def override(files, qa):
    """QA builds: set `en` of the given ids (build.py --qa ID=TEXT). Unknown ids are an error."""
    left = dict(qa)
    for doc in files.values():
        for e in doc["entries"]:
            if e["id"] in left:
                e["en"] = left.pop(e["id"])
    if left:
        raise SystemExit(f"--qa: unknown ids {sorted(left)}")


def text_of(e):
    return e["en"] or e["jp"]


FAR = 0xF700     # far jump: word $F700 + 24-bit CPU address (asm/vwf.asm vm_dispatch, menu_fetch)
FAR_LEN = 5
TEXT_AREA = (0x300000, 0x3E0000)  # moved strings (4 MB build); blocks.EXPANSION stops below it
PAD_MAX = 4      # a string shorter than its slot by fewer than FAR_LEN + 1 bytes is padded with spaces


def far(cpu):
    return FAR.to_bytes(2, "little") + cpu.to_bytes(3, "little")


def cpu_of(off):
    """LoROM CPU address ($80+ mirror) of a file offset."""
    return ((off >> 15) | 0x80) << 16 | (off & 0x7FFF) | 0x8000


class TextAlloc:
    """Bump allocator in TEXT_AREA; a string never crosses a 32 KB bank (the VM steps a 16-bit pointer)."""

    def __init__(self, area=TEXT_AREA):
        self.pos, self.end = area

    def take(self, n):
        if (self.pos & 0x7FFF) + n > 0x8000:
            self.pos = (self.pos | 0x7FFF) + 1
        if self.pos + n > self.end:
            raise ValueError("text area full")
        off, self.pos = self.pos, self.pos + n
        return off


def fit(enc, size, ret, alloc, writer, eid):
    """The bytes for a size-byte slot holding enc; ret = CPU address of the byte after the slot."""
    diff = size - len(enc)
    if diff == 0:
        return enc
    if 0 < diff <= PAD_MAX:
        return enc + EN.encode(" ") * (diff // 2)
    if diff > PAD_MAX:
        return (enc + far(ret)).ljust(size, b"\0")
    if size < FAR_LEN:
        raise ValueError(f"{eid}: {len(enc)} bytes for a {size}-byte slot, too short for a far jump")
    if alloc is None:
        raise ValueError(f"{eid}: {len(enc)} bytes for a {size}-byte slot (relocation needs the 4 MB build)")
    off = alloc.take(len(enc) + FAR_LEN)
    writer.put(off, enc + far(ret), f"moved:{eid}")
    return far(cpu_of(off)).ljust(size, b"\0")


def apply(orig, region, writer, files, alloc=None):
    """Splice every entry into region (block data) or writer (raw bytes). Strings longer than their slot move to
    TEXT_AREA through alloc, behind a far jump (and back); shorter ones jump over the rest. Returns the number of
    changed strings."""
    changed = 0
    bc = ByteCodec(orig, JP)
    for name, doc in files.items():
        src = doc["source"]
        if src["kind"] == "block":
            b = region.blocks[src["block"]]
            assert f"{b.orig_off:06X}" == src["file"], f"{name}: block {src['block']} moved; re-run extract.py"
            data = bytearray(b.data)
        for e in doc["entries"]:
            enc = (bc if src["kind"] == "names" else EN if e["en"] else JP).encode(text_of(e))
            size = e["size"]
            changed += bool(e["en"])
            if src["kind"] == "names":
                if len(enc) > e["max"]:
                    raise ValueError(f"{e['id']}: {len(enc)} bytes > field {e['max']}")
                enc = enc.ljust(size if len(enc) <= size else e["max"], b"\0")
                writer.put(int(e["file"], 16), enc, f"text:{e['id']}")
                continue
            a = int(e["addr"], 16)
            if src["kind"] == "block":  # every block runs decompressed at $7F:0000 (rooms, common, shops)
                data[a:a + size] = fit(enc, size, 0x7F0000 | (a + size), alloc, writer, e["id"])
            else:
                ret = int(src["bank"], 16) << 16 | (a + size)
                writer.put(int(e["file"], 16), fit(enc, size, ret, alloc, writer, e["id"]), f"text:{e['id']}")
        if src["kind"] == "block":
            b.data = bytes(data)
    return changed
