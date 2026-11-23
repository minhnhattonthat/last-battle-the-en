-- Debug only: skip the ending's waits on the sound CPU, so the credits start without the song playing out.
-- 02:DB40 (after "Fin") and 02:D716 (after the staff roll) poll APU port $2143 until the driver clears a bit.
--   --script tools/lua/skip_apu_wait.lua
local skips = { [0x02DB40] = 0x02DB47, [0x02D716] = 0x02D71E }
for from, to in pairs(skips) do
  local logged = false
  L.on_exec(from, from, function()
    local s = emu.getState()
    s["cpu.pc"] = to & 0xFFFF
    emu.setState(s)
    if not logged then L.log(string.format("SKIPWAIT %06X -> %06X f%d", from, to, L.frame)); logged = true end
  end)
end
