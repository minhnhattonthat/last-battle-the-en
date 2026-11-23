-- Log the CPU PC at the end of every frame in FROM..TO (step STEP, default 1): where a stuck screen spins.
--   --script tools/lua/pc_sample.lua --var FROM=14000 --var TO=14010 [--var STEP=1]
local step = STEP or 1
L.on_frame(function(f)
  if f >= FROM and f <= TO and (f - FROM) % step == 0 then
    local s = emu.getState()
    L.log(string.format("PC f%d %02X:%04X A=%04X X=%04X", f, s["cpu.k"], s["cpu.pc"], s["cpu.a"], s["cpu.x"]))
  end
end)
