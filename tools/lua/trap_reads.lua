-- Free-space check: log every CPU read of a free-space candidate (file offsets in RANGES, from
-- docs/re/compression.md), once per (offset, pc). DMA reads are not seen: pair with snes_dmalog.lua if needed.
-- Usage: --script tools/lua/trap_reads.lua
local ranges = RANGES or {
  {0x006F26, 0x007F48}, {0x016877, 0x018000}, {0x027BE9, 0x028000}, {0x02B5A0, 0x030000}, {0x0542F4, 0x058000},
  {0x0C8F5D, 0x0D0000}, {0x111837, 0x118000}, {0x11B8C8, 0x11C000}, {0x13DCC6, 0x140000},
}
local seen, hits = {}, 0
local function hook(addr, value)
  local off = L.rom_off(addr)
  for _, r in ipairs(ranges) do
    if off >= r[1] and off < r[2] then
      local s = emu.getState()
      local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
      local key = off * 16777216 + pc
      if not seen[key] then
        seen[key] = true
        hits = hits + 1
        if hits <= 200 then L.log(string.format("TRAP f%d pc=%06X off=%06X v=%02X", L.frame, pc, off, value)) end
      end
      return
    end
  end
end
for bank = 0, 0xFF do
  if bank < 0x7E or bank > 0x7F then
    emu.addMemoryCallback(L.safe(hook), emu.callbackType.read, (bank << 16) | 0x8000, (bank << 16) | 0xFFFF,
      emu.cpuType.snes, emu.memType.snesMemory)
  end
end
