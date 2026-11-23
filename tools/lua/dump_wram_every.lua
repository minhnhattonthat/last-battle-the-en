-- Dump WRAM to <out>/wram_<frame>.bin every EVERY frames between FROM and TO (for tools/ram diffing).
--   --script tools/lua/dump_wram_every.lua --var FROM=2400 --var TO=3600 --var EVERY=200
L.on_frame(function(f)
  if f >= FROM and f <= TO and (f - FROM) % EVERY == 0 then L.dump_ram("wram_" .. f .. ".bin") end
end)
