-- Battle status poke for The Last Battle (load after warp.lua; used by svc_cover.py bparty2).
-- The battle status of party unit i is unit +1 & 7 ($7E1298 + i*$28: 1 poison, 2 stun, 4 confusion; 29:9259 clears
-- it with "Poison cured" / "Can move again" / "Confusion cleared"). The units are built at battle start (29:B216),
-- so a READY poke can't set it: a scene pokes Kurt's record +1 ("@1901=01"), and once the battle units exist this
-- copies those low 3 bits into unit 0's +1, and holds them there every frame (session 29: set once at f2302, the
-- Cure Herb used later printed nothing, so something resets it between turns). Logs each time it had to rewrite.
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function w8(a, v) emu.write(a, v & 0xFF, emu.memType.snesMemory) end
local function r16(a) return rd(a) | (rd(a + 1) << 8) end

local since, writes = nil, 0
L.on_frame(function(n)
  if r16(0x7E1DDF) == 0xFFFF then since = nil; return end
  local st = rd(0x7E1901) & 7
  if st == 0 or r16(0x7E1298 + 0x10) == 0 then return end
  since = since or n
  if n - since < 60 then return end
  local cur = rd(0x7E1299)
  if cur & 7 ~= st then
    w8(0x7E1299, (cur & 0xF8) | st)
    writes = writes + 1
    if writes <= 20 then L.log(string.format("BSTATUS unit0+1 %02X -> %d f%d", cur, st, n)) end
  end
end)
