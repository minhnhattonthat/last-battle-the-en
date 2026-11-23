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
    from insert import MOVED_WINDOWS
    pool = {}
    for off, _o, _n, by in log:
        if by.startswith("pool:"):
            pool[by[5:]] = off
    out = []
    for doc in files.values():
        src = doc["source"]
        for e in doc["entries"]:
            if src["kind"] == "block":
                key = BLOCK_KEY | placed[src["block"]] << 16 | int(e["addr"], 16)
            elif src["kind"] == "names":
                key = int(e.get("field", e["file"]), 16)
            else:
                key = off = int(e["file"], 16)
                if e["id"] in pool:
                    key = pool[e["id"]]
                for lo, hi, _ptr in MOVED_WINDOWS:
                    if lo <= off < hi and f"window:{lo:06X}" in pool:
                        key = pool[f"window:{lo:06X}"] + off - lo
            out.append((e["id"], key))
    return out


def write(path, files, placed, log):
    lines = ["# id\tkey (tools/strings_tsv.py; block keys need textcover.py --mask 0xFFFFFFFFFFFF)"]
    lines += [f"{i}\t{k:X}" for i, k in rows(files, placed, log)]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
