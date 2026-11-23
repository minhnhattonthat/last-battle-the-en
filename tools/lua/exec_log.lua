-- Log the first N hits (default 3) of each CPU address in ADDRS (comma-separated hex string), with the frame.
--   --script tools/lua/exec_log.lua --var "ADDRS='02D598,02D71F'" [--var N=3]
local n = N or 3
for a in ADDRS:gmatch("[^,]+") do
  local addr = tonumber(a, 16)
  local c = 0
  L.on_exec(addr, addr, function()
    c = c + 1
    if c <= n then L.log(string.format("EXEC %06X f%d", addr, L.frame)) end
  end)
end
