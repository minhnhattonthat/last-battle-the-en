-- Log every change of the game mode ($7E000E, next mode $0010) and of the room ($002C) with the position
-- ($002E x, $0030 y, $0032 facing). Use with tools/debug/warp.lua to learn entry points and mode values.
local last, lastroom
local function r16(a) return emu.read(a, emu.memType.snesMemory) | (emu.read(a + 1, emu.memType.snesMemory) << 8) end
L.on_frame(function(n)
  local m = emu.read(0x7E000E, emu.memType.snesMemory) | (emu.read(0x7E0010, emu.memType.snesMemory) << 8)
  local room = r16(0x7E002C)
  if m ~= last or room ~= lastroom or (POS_EVERY and n % POS_EVERY == 0) then
    last, lastroom = m, room
    L.log(string.format("f%d mode $0E=%02X $10=%02X room=%d x=%d y=%d dir=%d", n, m & 0xFF, m >> 8, room,
      r16(0x7E002E), r16(0x7E0030), r16(0x7E0032)))
  end
end)
