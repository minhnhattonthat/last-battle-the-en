-- Log the stack (return addresses) at entry to each CPU address in ADDRS, once per distinct stack picture.
--   --script tools/lua/stack_log.lua --var "ADDRS='01FEAA,01FEE3'" [--var DEPTH=12]
-- Each line: STACK <addr> f<frame> sp=<SP> <DEPTH bytes from SP+1>. Read JSR returns as (word + 1) in the
-- caller's bank, JSL returns as 3 bytes.
local depth = DEPTH or 12
local seen = {}
for a in ADDRS:gmatch("[^,]+") do
  local addr = tonumber(a, 16)
  L.on_exec(addr, addr, function()
    local st = emu.getState()
    local sp = st["cpu.sp"]
    local b = {}
    for i = 1, depth do
      b[#b + 1] = string.format("%02X", emu.read(sp + i, emu.memType.snesMemory))
    end
    local key = string.format("%06X %s", addr, table.concat(b, " "))
    if not seen[key] then
      seen[key] = true
      L.log(string.format("STACK %06X f%d sp=%04X %s", addr, L.frame, sp, table.concat(b, " ")))
    end
  end)
end
