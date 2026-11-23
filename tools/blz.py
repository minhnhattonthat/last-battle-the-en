"""blz.py: the battle graphics LZ (bank 30 decoder 30:F5C1, docs/re/battle.md §Battle LZ).

Window: 2 KB ring at $7EC000, zero-filled before each stream, write position from 0. Control byte c:
  0xxxxxxx yyyyzzzz  copy (z + 2) bytes from window position (pos - (x << 4 | y)) & $7FF
  10nnnnnn           (n + 1) literal bytes
  11e mm nnn [lo]    fill: count = (n + 2), or ((n << 8 | lo) + 2) when e; pattern of mm+1 bytes follows
                     (mm = 0: 1 byte, 1: 2 bytes, 2: 3 bytes, 3: 4 bytes), repeated count times
The stream length comes from the load list (entry +7); the output starts with its own size word (the DMA length).

    python -X utf8 tools/blz.py decode FILE_OFFSET LENGTH OUT.bin     # FILE_OFFSET/LENGTH hex
    python -X utf8 tools/blz.py test                                  # roundtrip of the battle font"""
import sys

WIN = 0x800


def decode(src, length):
    out, win, wp, i = bytearray(), bytearray(WIN), 0, 0

    def put(b):
        nonlocal wp
        out.append(b)
        win[wp] = b
        wp = (wp + 1) % WIN

    while i < length - 1:  # the decoder loops while the pointer < start + length - 1
        c = src[i]
        if not c & 0x80:
            n1 = src[i + 1]
            i += 2
            off = ((c << 8 | n1) >> 4) & 0x7FF
            rp = (wp - off) % WIN
            for _ in range((n1 & 0x0F) + 2):
                put(win[rp])
                rp = (rp + 1) % WIN
        elif not c & 0x40:
            n = (c & 0x3F) + 1
            for b in src[i + 1:i + 1 + n]:
                put(b)
            i += 1 + n
        else:
            if c & 0x20:
                count = ((c & 7) << 8 | src[i + 1]) + 2
                i += 2
            else:
                count = (c & 7) + 2
                i += 1
            k = ((c >> 3) & 3) + 1
            pat = src[i:i + k]
            i += k
            for _ in range(count):
                for b in pat:
                    put(b)
    return bytes(out)


def encode(data):
    """Optimal parse (shortest stream) over copies, literal runs and 1-4 byte fills."""
    n = len(data)
    INF = 1 << 30
    cost = [INF] * (n + 1)
    step = [None] * (n + 1)
    cost[n] = 0
    where = {}
    for s in range(n - 1):
        where.setdefault(data[s:s + 2], []).append(s)
    for p in range(n - 1, -1, -1):
        best, bstep = INF, None
        # literal runs of 1..64
        for L in range(1, min(64, n - p) + 1):
            c = 1 + L + cost[p + L]
            if c < best:
                best, bstep = c, ("lit", L)
        # fills
        for k in (1, 2, 3, 4):
            pat = data[p:p + k]
            if len(pat) < k:
                break
            reps = 0
            q = p
            while q + k <= n and data[q:q + k] == pat and reps < 0x7FF + 2:
                reps += 1
                q += k
            for r in range(2, reps + 1):
                hdr = 1 if r <= 9 else 2
                c = hdr + k + cost[p + r * k]
                if c < best:
                    best, bstep = c, ("fill", k, r)
        # copies: offset 1..2047, length 2..17; sources before position 0 read the zero-filled window
        maxlen = min(17, n - p)
        if maxlen >= 2:
            key = data[p:p + 2]
            cands = [s for s in where.get(key, ()) if p - WIN < s < p]
            if key == b"\0\0":
                cands += [p - off for off in range(p + 1, min(WIN, p + 3))]
            for s in cands:
                L = 0
                while L < maxlen and (data[s + L] if s + L >= 0 else 0) == data[p + L]:
                    L += 1
                for m in range(2, L + 1):
                    c = 2 + cost[p + m]
                    if c < best:
                        best, bstep = c, ("copy", p - s, m)
        cost[p], step[p] = best, bstep
    out, p = bytearray(), 0
    while p < n:
        s = step[p]
        if s[0] == "lit":
            out.append(0x80 | (s[1] - 1))
            out += data[p:p + s[1]]
            p += s[1]
        elif s[0] == "fill":
            _, k, r = s
            mm = (k - 1) << 3
            if r <= 9:
                out.append(0xC0 | mm | (r - 2))
            else:
                v = r - 2
                out += bytes([0xE0 | mm | (v >> 8), v & 0xFF])
            out += data[p:p + k]
            p += r * k
        else:
            _, off, m = s
            v = off << 4 | (m - 2)
            out += bytes([v >> 8, v & 0xFF])
            p += m
    out.append(0)  # the decoder stops at start + length - 1: one byte of slack it never reads as a control
    return bytes(out)


def main(argv):
    if argv[:1] == ["decode"]:
        rom = open(sys.argv[0].rsplit("tools", 1)[0] + "rom/Last Battle, The (Japan).sfc", "rb").read()
        off, ln = int(argv[1], 16), int(argv[2], 16)
        open(argv[3], "wb").write(decode(rom[off:], ln))
        return 0
    if argv[:1] == ["test"]:
        from pathlib import Path
        rom = (Path(__file__).resolve().parents[1] / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
        d = decode(rom[0x150000:], 0xB34)
        e = encode(d)
        print(f"decoded {len(d)} bytes (size word {d[0] | d[1] << 8:#x}); original {0xB34}, re-encoded {len(e)}")
        assert decode(e, len(e)) == d
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
