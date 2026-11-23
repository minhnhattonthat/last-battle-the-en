-- Log every distinct ROM address read in one bank (both mirrors) between frames FROM..TO, with the PC.
-- Finds which rectangles/tables a screen draws from when snes_romreads.lua (one line per PC) hides them.
--   probe.py ... --script tools/lua/bank_reads.lua --var BANK=0x33 --var FROM=3470 --var TO=3760
-- Lines: "BR f<frame> pc=<pc> <addr> off=<file offset>".
local bank, from, to = BANK or 0x33, FROM or 0, TO or math.huge
local seen = {}
local function hook(addr, value)
  local f = L.frame
  if f < from or f > to then return end
  local a = addr & 0x7FFFFF
  if seen[a] then return end
  seen[a] = true
  local s = emu.getState()
  L.log(string.format("BR f%d pc=%02X%04X %06X off=%06X", f, s["cpu.k"], s["cpu.pc"], addr, L.rom_off(addr)))
end
for _, b in ipairs({bank, bank | 0x80}) do
  emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (b << 16) | 0x8000, (b << 16) | 0xFFFF,
    emu.cpuType.snes, emu.memType.snesMemory)
end
