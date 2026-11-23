"""insert.py: write script/*.json back into the ROM image during build.py (docs/re/text.md).

Each entry's text is `en` when set, else `jp`, encoded and spliced back at its address: script blocks into the
block's decompressed data (blocks.Region repacks and recompresses only changed blocks), raw banks and byte names
through Writer.put. With no English every write reproduces the original bytes (tests/test_identity.py).

Relocation (a string whose encoding changes size) needs the block reassembler and pointer rewrites: phase 5. Until
then a size change is an error, never a silent overwrite of the next string."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from textcodec import JP, ByteCodec  # noqa: E402

SCRIPT = ROOT / "script"


def load(script_dir=SCRIPT):
    return {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in sorted(Path(script_dir).glob("*.json"))}


def text_of(e):
    return e["en"] or e["jp"]


def apply(orig, region, writer, files):
    """Splice every entry into region (block data) or writer (raw bytes). Returns the number of changed strings."""
    changed = 0
    bc = ByteCodec(orig, JP)
    for name, doc in files.items():
        src = doc["source"]
        if src["kind"] == "block":
            b = region.blocks[src["block"]]
            assert f"{b.orig_off:06X}" == src["file"], f"{name}: block {src['block']} moved; re-run extract.py"
            data = bytearray(b.data)
        for e in doc["entries"]:
            enc = (bc if src["kind"] == "names" else JP).encode(text_of(e))
            size = e["size"]
            if src["kind"] == "names":
                if len(enc) > e["max"]:
                    raise ValueError(f"{e['id']}: {len(enc)} bytes > field {e['max']}")
                enc = enc.ljust(size if len(enc) <= size else e["max"], b"\0")
                size = len(enc)  # the whole 8-byte field is the name's (0-terminated when shorter)
            if len(enc) != size:
                raise NotImplementedError(f"{e['id']}: {len(enc)} bytes for a {size}-byte slot (relocation: phase 5)")
            changed += bool(e["en"])
            if src["kind"] == "block":
                a = int(e["addr"], 16)
                data[a:a + size] = enc
            else:
                writer.put(int(e["file"], 16), enc, f"text:{e['id']}")
        if src["kind"] == "block":
            b.data = bytes(data)
    return changed
