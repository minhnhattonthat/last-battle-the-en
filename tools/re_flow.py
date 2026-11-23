"""re_flow.py: flow-following 65816 walk from an entry point (bank-local), listing every instruction that touches the
script pointer (dp $10-$12, [$10]) and every subroutine it reaches that does.

    python -X utf8 tools/re_flow.py 01CD4B [01E14D ...] [--m8] [--x8] [--all]
Follows branches, BRA/JMP abs, JSR abs (recursively, same bank). Stops at RTS/RTL/RTI. JSR (abs,x) and JSL are
listed but not followed. M/X: REP/SEP tracked along each path; PLP keeps the current state (good enough for these
handlers, which PHP/PLP in pairs). --all prints the whole reachable listing."""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

sys.path.insert(0, str(Path(SKILL) / "scripts"))
from dis65816 import disasm  # noqa: E402

ROM = (ROOT / "rom" / "Last Battle, The (Japan).sfc").read_bytes()
PTR = re.compile(r"\[\$10\]|(?<!#)\$1[012]\b|\$000?1[012]\b")


def walk(entry, m8=False, x8=False, seen=None):
    """Returns ({addr: line}, set of JSR targets)."""
    lines, calls, todo = {}, set(), [(entry, m8, x8)]
    seen = set() if seen is None else seen
    while todo:
        addr, m, x = todo.pop()
        while (addr, m, x) not in seen:
            seen.add((addr, m, x))
            ln = disasm(ROM, addr, 1, m8=m, x8=x)[0]
            raw = ln[17:29].split()  # "BB:AAAA  PPPPPP  raw(12) MN arg"
            ins = ln[30:].split(";")[0].split()
            mn, arg = ins[0], (ins[1] if len(ins) > 1 else "")
            size = len(raw)
            lines[addr] = ln
            if mn == "REP":
                v = int(raw[1], 16)
                m, x = m and not v & 0x20, x and not v & 0x10
            elif mn == "SEP":
                v = int(raw[1], 16)
                m, x = m or bool(v & 0x20), x or bool(v & 0x10)
            nxt = (addr & 0xFF0000) | ((addr + size) & 0xFFFF)
            if mn in ("RTS", "RTL", "RTI", "STP"):
                break
            if mn in ("BRA", "BRL", "JMP") and arg.startswith("$") and len(arg) == 5:
                addr = (addr & 0xFF0000) | int(arg[1:], 16)
                continue
            if mn in ("JMP", "JML"):
                break  # indirect / long: not followed
            if mn.startswith("B") and mn not in ("BIT", "BRK") and arg.startswith("$"):
                todo.append(((addr & 0xFF0000) | int(arg[1:], 16), m, x))
            if mn == "JSR" and arg.startswith("$") and len(arg) == 5:
                calls.add((addr & 0xFF0000) | int(arg[1:], 16))
            addr = nxt
    return lines, calls


def analyse(entry, m8, x8, show_all, depth=0, done=None):
    done = set() if done is None else done
    if entry in done:
        return
    done.add(entry)
    lines, calls = walk(entry, m8, x8)
    ins = {a: lines[a][30:].split(";")[0].strip() for a in lines}
    hits = [lines[a] for a in sorted(lines) if PTR.search(ins[a])]
    other = sorted({i for i in ins.values() if i.split()[0] in ("JSL", "JML") or
                    ("(" in i or "[" in i) and i.split()[0] in ("JSR", "JMP")})
    pad = "  " * depth
    print(f"{pad}== {entry >> 16:02X}:{entry & 0xFFFF:04X}  {len(lines)} instr, ptr refs {len(hits)}; "
          f"calls {' '.join(f'{c & 0xFFFF:04X}' for c in sorted(calls))}; unfollowed {', '.join(other)}")
    for h in (lines[a] for a in sorted(lines)) if show_all else hits:
        print(pad + "   " + h[:72])
    for c in sorted(calls):
        analyse(c, m8, x8, show_all, depth + 1, done)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("entries", nargs="+")
    ap.add_argument("--m8", action="store_true")
    ap.add_argument("--x8", action="store_true")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    for e in a.entries:
        analyse(int(e, 16), a.m8, a.x8, a.all)


if __name__ == "__main__":
    main()
