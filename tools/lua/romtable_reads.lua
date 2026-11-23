-- Log every CPU read of a ROM file range LO..HI (file offsets, LoROM) with PC, A/X/Y and DP, deduped by (pc, off).
-- Usage: --script tools/lua/romtable_reads.lua --var LO=0xD0081 --var HI=0xD0420
local lo, hi = LO or 0xD0081, HI or 0xD0420
local seen = {}
local function hook(addr, value)
  local off = L.rom_off(addr)
  if off < lo or off > hi then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local key = string.format("%06X/%06X", pc, off)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("f%d pc=%06X off=%06X v=%02X A=%04X X=%04X Y=%04X D=%04X DB=%02X", L.frame, pc, off, value,
    s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.d"], s["cpu.dbr"]))
end
local b0 = (lo >> 15)
local b1 = (hi >> 15)
for b = b0, b1 do
  for _, bank in ipairs({ b, b | 0x80 }) do
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
