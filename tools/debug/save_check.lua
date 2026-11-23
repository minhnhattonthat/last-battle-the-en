-- After loading a save, assert the WRAM values save.py wrote. Logs "SAVECHECK ok ..." or raises an error (exit 2).
--   --script tools/debug/save_check.lua --var AT=2400 --var ROOM=77 --var MONEY=9999999 [--var FLAG=0x10]
local function rd(a) return emu.read(0x7E0000 + a, emu.memType.snesMemory) end
local function r16(a) return rd(a) | (rd(a + 1) << 8) end
L.on_frame(function(f)
  if f ~= AT then return end
  local room, money = r16(0x2C), rd(0x1DD1) | (rd(0x1DD2) << 8) | (rd(0x1DD3) << 16)
  local msg = string.format("room=%d x=%d y=%d money=%d party=%d", room, r16(0x2E), r16(0x30), money, r16(0x3E))
  if FLAG then msg = msg .. string.format(" flag%X=%d", FLAG, rd(0x200 + FLAG)) end
  local bad = (ROOM and room ~= ROOM) or (MONEY and money ~= MONEY) or (FLAG and rd(0x200 + FLAG) ~= 1)
  if bad then error("SAVECHECK fail " .. msg) end
  L.log("SAVECHECK ok " .. msg)
end)
