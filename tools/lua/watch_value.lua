-- Log writes into LO..HI whose value differs from SKIP (default 0xFF), first N per (pc, value).
--   --script tools/lua/watch_value.lua --var LO=0x7E1DDF --var HI=0x7E1DE0 [--var SKIP=0xFF] [--var N=4]
local skip, n = SKIP or 0xFF, N or 4
local count = {}
L.on_write(LO, HI, function(addr, value)
  if value == skip then return end
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  local k = pc * 256 + value
  count[k] = (count[k] or 0) + 1
  if count[k] <= n then
    L.log(string.format("f%d pc=%06X w %06X=%02X A=%04X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, addr, value,
      s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
  end
end)
