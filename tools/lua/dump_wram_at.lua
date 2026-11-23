-- Dump WRAM ($7E0000-$7FFFFF) to <out>/wram_<frame>.bin at frame AT.   --var AT=300
L.on_frame(function(f)
  if f == AT then
    L.dump_ram("wram_" .. f .. ".bin")
    L.log("dumped wram at " .. f)
  end
end)
