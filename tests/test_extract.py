"""Phase 4 extraction (tools/extract.py, docs/re/text.md):
- roundtrip: re-encoding every extracted string's jp gives the original bytes (blocks, raw banks, byte names);
- script/*.json is in sync with a fresh extraction (ids, addresses, sizes, jp);
- coverage against the ORIGINAL ROM: every walked glyph and every text run in the script blocks and raw text
  areas sits inside a string or a known data range; no strings overlap;
- the build splices script/ back (identity with no English) and refuses a size change until relocation exists."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Last Battle, The (Japan).sfc"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

need_rom = pytest.mark.skipif(not ROM.is_file(), reason="no ROM in rom/")


@pytest.fixture(scope="module")
def ext():
    import extract
    rom = ROM.read_bytes()
    return rom, extract.extract_all(rom)


def test_codec_roundtrip_synthetic():
    from textcodec import JP
    data = bytes.fromhex("3503 00FE 38FA 0D03 0100 FFFC 1234")  # glyph, nl, actor, dup/odd glyph, tile, wait, ctrl
    text = JP.decode(data)
    assert "{nl}" in text and "{actor}" in text and "{wait}" in text and "{0001}" in text and "{3412}" in text
    assert JP.encode(text) == data


@need_rom
def test_roundtrip(ext):
    import blocks
    from textcodec import JP, ByteCodec, bg3_jp
    rom, files = ext
    region = blocks.unpack(rom)
    bc = ByteCodec(rom, JP)
    codec = {"names": bc, "bg3": bg3_jp(rom)}
    n = 0
    for name, doc in files.items():
        src = doc["source"]
        for e in doc["entries"]:
            if src["kind"] == "block":
                a = int(e["addr"], 16)
                want = region.blocks[src["block"]].orig_data[a:a + e["size"]]
                got = JP.encode(e["jp"])
            else:
                f = int(e["file"], 16)
                want = rom[f:f + e["size"]]
                got = codec.get(src["kind"], JP).encode(e["jp"])
            assert got == want, e["id"]
            n += 1
    assert n > 2500


@need_rom
def test_script_dir_in_sync(ext):
    _, files = ext
    on_disk = {p.stem for p in (ROOT / "script").glob("*.json")}
    assert on_disk == set(files), "re-run: python -X utf8 tools/extract.py dump --force"
    for name, doc in files.items():
        disk = json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8"))
        assert disk["source"] == doc["source"], name
        key = [(e["id"], e.get("addr"), e.get("file"), e["size"], e["jp"]) for e in doc["entries"]]
        assert [(e["id"], e.get("addr"), e.get("file"), e["size"], e["jp"]) for e in disk["entries"]] == key, name


@need_rom
def test_bg3_strings(ext):
    """BG3 tile strings: the menu prompts and labels the marker tour showed in Japanese are extracted, each one inside
    its write range, and English encodes to BG3 tiles (capitals, digits, the font_bg3 lowercase, space $93)."""
    from textcodec import bg3_en
    rom, files = ext
    es = files["menus"]["entries"]
    jp = {e["jp"].strip() for e in es}
    for want in ("どうしますか？", "はい", "いいえ", "モノラル", "ステレオ", "どのファイルに セ－ブしますか？",
                 "{0112} どのファイルを ロ－ドしますか？", "よろしいですか？"):
        assert want in jp, want
    assert all(0x20600 <= int(e["file"], 16) and int(e["file"], 16) + e["size"] <= 0x22CA7 for e in es)
    assert bg3_en().encode("Ab1 z?{nl}") == bytes.fromhex("0b00 2600 0200 9300 3e00 4400 00fe".replace(" ", ""))


@need_rom
def test_coverage(ext):
    import extract
    rom, files = ext
    assert extract.coverage(rom, files) == []
    ids = [e["id"] for doc in files.values() for e in doc["entries"]]
    assert len(ids) == len(set(ids))


@need_rom
def test_insert_size_change_refused(tmp_path):
    import build
    d = tmp_path / "script"
    d.mkdir()
    src = json.loads((ROOT / "script" / "bank04.json").read_text(encoding="utf-8"))
    src["entries"][0]["en"] = "x" * (src["entries"][0]["size"] // 2 + 1)
    (d / "bank04.json").write_text(json.dumps(src, ensure_ascii=False), encoding="utf-8")
    with pytest.raises(ValueError):  # the 2 MB build has nowhere to move it
        build.build(tmp_path / "x.sfc", script_dir=d, asm=False)


@need_rom
def test_insert_same_size_edit(tmp_path):
    """A same-size edit in a block and in bank 04 lands in the ROM (block recompressed, raw bytes put)."""
    import blocks
    import build
    from textcodec import EN as JP  # English text goes through the EN codec
    d = tmp_path / "script"
    d.mkdir()
    for name in ("bank04", "r010"):
        doc = json.loads((ROOT / "script" / f"{name}.json").read_text(encoding="utf-8"))
        e = doc["entries"][0]
        e["en"] = "A" * (e["size"] // 2)
        (d / f"{name}.json").write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    rom, log = build.build(tmp_path / "x.sfc", script_dir=d)
    b04 = json.loads((d / "bank04.json").read_text(encoding="utf-8"))["entries"][0]
    f = int(b04["file"], 16)
    assert rom[f:f + b04["size"]] == JP.encode(b04["en"])
    r10 = json.loads((d / "r010.json").read_text(encoding="utf-8"))
    import lz
    slot = blocks.unpack(ROM.read_bytes()).blocks[r10["source"]["block"]].slots[0]
    data, _ = lz.decompress(rom, blocks.to_file(blocks.read_ptr(rom, slot)))
    a = int(r10["entries"][0]["addr"], 16)
    assert data[a:a + r10["entries"][0]["size"]] == JP.encode(r10["entries"][0]["en"])
    assert any(by.startswith("block") for _, _, _, by in log)
