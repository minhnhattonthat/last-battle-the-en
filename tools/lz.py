"""lz.py: the game's LZ codec (decompressor at 00:83A7, byte reader 00:8417). See docs/re/compression.md.

Stream: u16 L, u16 (unknown, kept), then commands until L+2 bytes in total have been read (header included).
Commands (c = command byte):
  c < $80        back-reference: b = next byte; w = c<<8 | b; len = (b & 15) + 2; dist = (w >> 4) & $7FF;
                 copy len bytes from ring[(pos - dist) & $7FF ...]. The game reads the whole run from the ring
                 BEFORE writing it back, so a run that overlaps its own output repeats stale ring bytes.
  $80-$BF        literal: (c & $3F) + 1 bytes follow.
  $C0-$FF        fill: n = (c & 7) [+ next byte as low 8 bits when c & $20, n = (c & 7) << 8 | byte]; n += 2;
                 width = ((c >> 3) & 3) + 1 bytes of pattern follow; the pattern is written n times.
Ring: 2 KB, zero-filled at start, position 0. Every output byte goes into the ring.
Byte reads run through LoROM banks: after $FFFF the reader goes to the next bank at $8000."""

RING = 0x800


def lorom_off(addr):
    return ((addr & 0x7F0000) >> 1) | (addr & 0x7FFF)


def decompress(rom, off):
    """Decompress the block at file offset off. Returns (data, compressed size in bytes)."""
    total = int.from_bytes(rom[off:off + 2], "little") + 2
    p = off + 4
    end = off + total
    ring = bytearray(RING)
    pos = 0
    out = bytearray()

    def emit(bs):
        nonlocal pos
        for v in bs:
            out.append(v)
            ring[pos] = v
            pos = (pos + 1) & (RING - 1)

    while p < end:
        c = rom[p]
        p += 1
        if c < 0x80:
            b = rom[p]
            p += 1
            w = (c << 8) | b
            n = (b & 15) + 2
            src = (pos - ((w >> 4) & 0x7FF)) & (RING - 1)
            run = bytes(ring[(src + i) & (RING - 1)] for i in range(n))
            emit(run)
        elif c < 0xC0:
            n = (c & 0x3F) + 1
            emit(rom[p:p + n])
            p += n
        else:
            n = c & 7
            if c & 0x20:
                n = (n << 8) | rom[p]
                p += 1
            n += 2
            width = ((c >> 3) & 3) + 1
            pat = rom[p:p + width]
            p += width
            emit(pat * n)
    return bytes(out), total


MAX_LIT = 0x40          # literal run: (c & $3F) + 1
MAX_REF = 17            # back-reference: (b & 15) + 2
MAX_DIST = RING - 1     # 11-bit distance; 0 would read the byte 2 KB back
MAX_FILL = 0x7FF + 2    # long fill count: 11 bits + 2
WINDOW = MAX_DIST


def _match_lengths(buf, start):
    """Longest non-overlapping back-reference at each position of buf[start:] (buf = zero prefix + data).

    Distances are >= the length, so the run never reads bytes the same command writes: the game reads the whole run
    before writing it, so an overlapping run would repeat stale ring bytes. The zero prefix stands for the zero-filled
    ring, which the game's decoder lets a block reference before its first byte."""
    n = len(buf)
    best = [0] * n
    chains = {}
    for i in range(n - 1):
        key = buf[i:i + 2]
        if i >= start:
            top, lo = 0, i - WINDOW
            cands = chains.get(key, ())
            for j in reversed(cands):
                if j < lo:
                    break
                limit = min(MAX_REF, i - j, n - i)
                if limit <= top or limit < 2:
                    continue
                k = 2
                while k < limit and buf[j + k] == buf[i + k]:
                    k += 1
                if k > top:
                    top = k
                    if top == MAX_REF:
                        break
            best[i] = top if top >= 2 else 0
        chains.setdefault(key, []).append(i)
    return best


def compress(data, w1=None):
    """Compress data into a stream decompress() reads back exactly. Optimal parse over the command costs.

    The original tool's parse is not reproduced (it is not greedy); the build reuses each unchanged block's original
    bytes, so only edited blocks go through here. w1: the second header word (default L - 2, as in 322 of 324
    original blocks)."""
    pre = min(WINDOW, RING)
    buf = bytes(pre) + bytes(data)
    n = len(data)
    refs = _match_lengths(buf, pre)
    INF = 1 << 60
    cost = [INF] * (n + 1)
    choice = [None] * (n + 1)
    cost[n] = 0
    for i in range(n - 1, -1, -1):
        b = cost[i]
        ch = None
        # literal runs
        for k in range(1, min(MAX_LIT, n - i) + 1):
            c = 1 + k + cost[i + k]
            if c < b:
                b, ch = c, ("L", k)
        # back-references: every length up to the longest is available at the same distance
        m = refs[pre + i]
        for k in range(2, m + 1):
            c = 2 + cost[i + k]
            if c < b:
                b, ch = c, ("R", k)
        # fills of width 1-4
        for w in range(1, 5):
            if i + 2 * w > n:
                break
            pat = data[i:i + w]
            reps = 1
            while reps < MAX_FILL and i + (reps + 1) * w <= n and data[i + reps * w:i + (reps + 1) * w] == pat:
                reps += 1
            for r in range(2, reps + 1):
                c = (1 if r <= 9 else 2) + w + cost[i + r * w]
                if c < b:
                    b, ch = c, ("F", w, r)
        cost[i], choice[i] = b, ch
    # emit; a back-reference needs its distance, found again here
    out = bytearray()
    i = 0
    while i < n:
        ch = choice[i]
        if ch[0] == "L":
            k = ch[1]
            out.append(0x80 | (k - 1))
            out += data[i:i + k]
            i += k
        elif ch[0] == "R":
            k = ch[1]
            p = pre + i
            lo = max(0, p - MAX_DIST)
            j = buf.rfind(buf[p:p + k], lo, p)  # nearest source wholly before p
            assert j >= 0 and p - j >= k, (i, k)
            dist = p - j
            w = (dist << 4) | (k - 2)
            out += bytes([w >> 8, w & 0xFF])
            i += k
        else:
            _, w, r = ch
            if r <= 9:
                out.append(0xC0 | ((w - 1) << 3) | (r - 2))
            else:
                v = r - 2
                out += bytes([0xE0 | ((w - 1) << 3) | (v >> 8), v & 0xFF])
            out += data[i:i + w]
            i += r * w
    L = len(out) + 2
    if L > 0xFFFF:
        raise ValueError(f"compressed stream too long ({L} bytes)")
    hdr = L.to_bytes(2, "little") + ((L - 2) if w1 is None else w1).to_bytes(2, "little")
    return hdr + bytes(out)


if __name__ == "__main__":
    import sys
    from pathlib import Path
    rom = (Path(__file__).resolve().parents[1] / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
    data, size = decompress(rom, int(sys.argv[1], 16))
    print(f"{len(data)} bytes out, {size} in")
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_bytes(data)
