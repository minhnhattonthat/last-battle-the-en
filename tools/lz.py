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


if __name__ == "__main__":
    import sys
    from pathlib import Path
    rom = (Path(__file__).resolve().parents[1] / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
    data, size = decompress(rom, int(sys.argv[1], 16))
    print(f"{len(data)} bytes out, {size} in")
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_bytes(data)
