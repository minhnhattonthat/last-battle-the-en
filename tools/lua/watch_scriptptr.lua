-- Log writes to the text/script pointer $7E0C10-$7E0C12 (DP $0C00, [$10]) that are not the engine's own INC $10,
-- with PC and the 24-bit pointer after the write. Finds how scripts are started (pointer tables, jump codes).
local last = {}
L.on_write(0x7E0C10, 0x7E0C12, function(addr, value)
  local s = emu.getState()
  local pc = (s["cpu.k"] << 16) | s["cpu.pc"]
  if pc == 0x01B7A3 or pc == 0x01B7A5 then return end -- INC $10 x2 in the main loop
  local key = string.format("%06X", pc)
  last[key] = (last[key] or 0) + 1
  if last[key] <= 4 then
    L.log(string.format("f%d pc=%06X w %06X=%02X", L.frame, pc, addr, value))
  end
end)
