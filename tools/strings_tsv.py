"""build/strings.tsv for the text-coverage gate ($SKILL/scripts/textcover.py): one `id<TAB>hex key` per string, the key
being what tools/debug/textcover.lua logs when the game reads the string's first byte.

- ROM strings (raw, bg3, battle, names): the file offset of the first byte the game reads. A string in place, or one
  moved behind a far jump, is read from its own slot first; a string the build moved whole and repointed (bank pools,
  moved windows) is read from its new place, taken from the build's write log.
- Block strings (room, common and service scripts, LZ blocks decompressed over $7F:0000): every block lands at the
  same WRAM, so the key is BLOCK_KEY | (file offset of the block's stream in this build) << 16 | offset in the block.
  textcover.lua remembers the stream of the last decompression to $7F (00:83A7) and keys each $7F read the same way.

Run the report with `--mask 0xFFFFFFFFFFFF` (the default 32-bit mask would cut the block keys)."""
BLOCK_KEY = 1 << 40


def rows(files, placed, log):
    """files: insert.load() (after the build applied them); placed: Region.pack()'s {block index: file offset};
    log: Writer.log, (offset, orig, new, by) per write. Returns [(id, key)]."""
    from insert import MOVED_WINDOWS, NAMES_AREA, NAME_KIND
    pool, names = {}, None
    for off, _o, new, by in log:
        if by.startswith("pool:"):
            pool[by[5:]] = off
        elif by == "names:en":
            names = (off, bytes(new))

    def name_key(kind, n):
        """File offset of the English name's ASCII in NAMES_AREA (asm nm_*: pointer table after the 128-word BG3
        map, one word per kind * 256 + n)."""
        base, blob = names
        p = int.from_bytes(blob[0x100 + 2 * ((kind - 1) * 256 + n):][:2], "little")
        return base + p - 0x8000

    out = []
    for doc in files.values():
        src = doc["source"]
        for n, e in enumerate(doc["entries"], 1):
            # spell names: the menus read them from the character records in WRAM, never from the ROM slot, so the
            # first read of a spell is its English name in NAMES_AREA (escape kind 2, n = position in spells.json)
            if src["kind"] == "names" and doc is files.get("spells") and names and e.get("en"):
                assert names[0] == NAMES_AREA
                out.append((e["id"], name_key(NAME_KIND["spells"], n)))
                continue
            out.append((e["id"], _key(src, e, pool, placed, MOVED_WINDOWS)))
    return out


def _key(src, e, pool, placed, moved):
    if src["kind"] == "block":
        return BLOCK_KEY | placed[src["block"]] << 16 | int(e["addr"], 16)
    if src["kind"] == "names":
        return int(e.get("field", e["file"]), 16)
    key = off = int(e["file"], 16)
    if e["id"] in pool:
        key = pool[e["id"]]
    for lo, hi, _ptr in moved:
        if lo <= off < hi and f"window:{lo:06X}" in pool:
            key = pool[f"window:{lo:06X}"] + off - lo
    return key


def write(path, files, placed, log):
    lines = ["# id\tkey (tools/strings_tsv.py; block keys need textcover.py --mask 0xFFFFFFFFFFFF)"]
    lines += [f"{i}\t{k:X}" for i, k in rows(files, placed, log)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
