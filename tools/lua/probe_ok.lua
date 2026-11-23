-- Setup check: proves --script runs and L.log reaches log.txt.
L.on_frame(function(n) if n == 100 then L.log("probe ok frame 100") end end)
