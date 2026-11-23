-- Log the first frame each listed ROM rectangle (text string) is read, and every later frame it is read again
-- at most once per 60 frames. RECTS = {{off, size, "id"}, ...} (file offsets, LoROM), passed by
-- tools/battle_cover.py. Lines: "RECT <id> f<frame> pc=<pc>".
local rects = RECTS or {}
local last = {}
local function lorom(off)
  return ((off // 0x8000) << 16) | 0x8000 | (off % 0x8000)
end
for _, r in ipairs(rects) do
  local off, size, id = r[1], r[2], r[3]
  local function hook(addr, value)
    local f = L.frame
    if last[id] and f - last[id] < 60 then return end
    last[id] = f
    local s = emu.getState()
    L.log(string.format("RECT %s f%d pc=%02X%04X", id, f, s["cpu.k"], s["cpu.pc"]))
  end
  local a = lorom(off)
  local b = lorom(off + size - 1)
  for _, mirror in ipairs({0, 0x800000}) do
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, a + mirror, b + mirror,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
