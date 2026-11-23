"""Print scenes.tsv rows: places (room ids from the place-name table 0x232FA) and E4 services."""
import re
import sys
sys.path.insert(0, "tools")
d = open("rom/Last Battle, The (Japan).sfc", "rb").read()
o = 0x232FA
seen = {}
while True:
    room = d[o] | d[o + 1] << 8
    if room == 0xFFFF:
        break
    ptr = d[o + 2] | d[o + 3] << 8
    seen.setdefault(ptr, []).append(room)
    o += 4
T = "\t"
for i, (ptr, rooms) in enumerate(sorted(seen.items())):
    r = rooms[0]
    print(T.join([f"place_{i:02d}", f"0x{r:02X}", "10", "8", "2", "-", "-", "60 -",
                  f"place-name table entry ptr {ptr:04X}, rooms {' '.join('%02X' % x for x in rooms)}"]))
kinds = {"00": "shop", "01": "shop", "02": "shop", "03": "shop", "04": "inn", "05": "inn", "06": "healer",
         "07": "healer"}
done = set()
for line in open("work/e4_all.txt", encoding="utf-8"):
    m = re.search(r"r(\d+) .*E4([0-9A-F]{2}) ([0-9A-F]{2})", line)
    if not m or (m.group(2), m.group(3)) in done:
        continue
    done.add((m.group(2), m.group(3)))
    lo, arg = m.group(2), m.group(3)
    kind = kinds.get(lo, "service")
    keys = "30 -;6 a;60 -;6 a;60 -;6 a;60 -;6 a;90 -"
    print(T.join([f"svc_{lo}_{arg}", "0x4D", "10", "6", "2", "-", f"ops:{lo}E4{arg}", keys,
                  f"{kind}: op E4{lo} {arg} (top-table entry {0x0E + int(lo, 16)}), used in room {int(m.group(1))}"]))
