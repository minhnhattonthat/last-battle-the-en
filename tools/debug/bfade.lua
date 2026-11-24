-- Force the "Magic faded away" roll for a Seal Stone / Seal Tome used in battle (load after warp.lua).
-- 29:89BD-89CA rolls JSL 2A:9D70 against $55 (stone) or $40 (tome); 29:89CD BCS skips the fade. Clearing carry
-- there makes the item fade every use, so bt_186512 shows without waiting on the RNG (session 30).
local hits = 0
L.on_exec(0x2989CD, 0x2989CD, function()
  local s = emu.getState()
  emu.setState({["cpu.ps"] = s["cpu.ps"] & 0xFE})
  hits = hits + 1
  if hits <= 5 then L.log(string.format("BFADE carry cleared f%d", L.frame)) end
end)
