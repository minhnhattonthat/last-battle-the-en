"""Recon: dump a raw ROM range as script words, one line per string (split after each FFxx), with file offsets.

    python -X utf8 tools/re_dumptext.py 23000 24800 [--odd] [--width 100]

Words that are not glyphs or controls print as <XXXX>, so tables and code between strings stand out.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from re_textscan import ROM, load_names, word_text  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("start")
    ap.add_argument("end")
    ap.add_argument("--width", type=int, default=100)
    a = ap.parse_args()
    rom = ROM.read_bytes()
    names = load_names()
    s, e = int(a.start, 16), int(a.end, 16)
    line, at = [], s
    for p in range(s, e - 1, 2):
        w = rom[p] | rom[p + 1] << 8
        if 0x300 <= w <= 0x7D0 or w >= 0x8000:
            line.append(word_text(w, names))
        else:
            line.append(f"<{w:04X}>")
        if w >> 8 == 0xFF or len(line) >= 40:
            print(f"{at:06X} {''.join(line)}"[:a.width])
            line, at = [], p + 2
    if line:
        print(f"{at:06X} {''.join(line)}"[:a.width])


if __name__ == "__main__":
    main()
