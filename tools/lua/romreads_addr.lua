-- Log each distinct ROM address read between frames FROM..TO (with PC), dedup by address, not by PC.
-- Finds text streams read one byte per character. Usage: --script tools/lua/romreads_addr.lua --var FROM=1005 --var TO=1030
local from, to = FROM or 0, TO or math.huge
local seen = {}
local function hook(addr, value)
  if L.frame < from or L.frame > to then return end
  local off = L.rom_off(addr)
  if seen[off] then return end
  seen[off] = true
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  L.log(string.format("f%d pc=%06X off=%06X v=%02X", L.frame, pc, off, value))
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
