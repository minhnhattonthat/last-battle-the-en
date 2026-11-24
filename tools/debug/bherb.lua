-- Force the status a Cure Herb finds on its target (load after warp.lua; --var BST=1 poison, 4 confusion).
-- 29:926A-926D reads the target unit +1 & 7, 29:9270 PHAs it and jumps on it (DE36 poison cured, DE48 confusion
-- cleared). The battle resets a poked unit status between turns (bstatus.lua), so set A here instead (session 30).
local st = BST or 1
local hits = 0
L.on_exec(0x299270, 0x299270, function()
  local s = emu.getState()
  emu.setState({["cpu.a"] = (s["cpu.a"] & 0xFF00) | st})
  hits = hits + 1
  if hits <= 5 then L.log(string.format("BHERB status %d f%d", st, L.frame)) end
end)
