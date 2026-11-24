-- Text coverage: force the title's LOAD to fail so "the file has been erased" (b04_B966, $04:B966) prints.
-- 01:8383 JSL 03:F80B (A = 2: load slot $0884) returns A = 1 on success; 01:8387 CMP #$0001 / BEQ, else the title
-- runs the bank-04 script at $04:B966. Hook the CMP and set A = 0. Use after warp.lua with a scene that loads FILE1:
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='load_file1'" --sav work/saves/base_file1.srm
--          --script tools/debug/load_fail.lua [--script tools/debug/textcover.lua --var "RANGES='...'"]
L.on_exec(0x018387, 0x018387, function()
  local s = emu.getState()
  s["cpu.a"] = 0
  emu.setState(s)
  L.log("LOADFAIL f" .. L.frame)
end)
