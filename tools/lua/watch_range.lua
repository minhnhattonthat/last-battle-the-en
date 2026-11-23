-- Log the first N writes (default 12) per PC into WRAM range LO..HI, with frame and value.
--   --script tools/lua/watch_range.lua --var LO=0x7F0000 --var HI=0x7F000F [--var N=12]
local n = N or 12
local count = {}
L.on_write(LO, HI, function(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  count[pc] = (count[pc] or 0) + 1
  if count[pc] <= n then
    L.log(string.format("f%d pc=%06X w %06X=%02X A=%04X X=%04X Y=%04X DB=%02X D=%04X", L.frame, pc, addr, value,
      s["cpu.a"], s["cpu.x"], s["cpu.y"], s["cpu.dbr"], s["cpu.d"]))
  end
end)
