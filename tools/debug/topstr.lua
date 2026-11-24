-- Show one string of a common-format block (shops, inns, healers: top14..top28; the common block of op E5) out of its
-- story context. Load after warp.lua and textcover.lua, with the op that loads the block as OPS (E4 lo arg / E5 lo),
-- STREAM = the block's file offset and TOPSTR = the string's offset in the decompressed block (hex; the strings.tsv
-- key is 1<<40 | STREAM<<16 | TOPSTR, same build).
-- The decompressor 00:83A7 (source $AC-$AE, absolute) runs some frames after the loader queues it (01:FDDF) and exits
-- at 00:8410. These blocks start with a word table of script pointers (0 = unused slot) that the op runs from; when
-- the first decompression of STREAM ends, every used slot is pointed at TOPSTR, so whichever script runs prints the
-- string as inline text. Later loads (the room-block reload) are left alone. Logs TOPSTR <off> slots <n> f<frame>.
if not TOPSTR then return end
local off, stream = tonumber(TOPSTR, 16), tonumber(STREAM, 16)
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function w8(a, v) emu.write(a, v & 0xFF, emu.memType.snesMemory) end
local pending, done = false, false
for _, b in ipairs({0x000000, 0x800000}) do
  L.on_exec(b | 0x83A7, b | 0x83A7, function()
    if done or rd(0x7E00B2) ~= 0x7F or rd(0x7E00B0) ~= 0 or rd(0x7E00B1) ~= 0 then return end
    pending = L.rom_off(rd(0x7E00AC) | rd(0x7E00AD) << 8 | rd(0x7E00AE) << 16) == stream
  end)
  L.on_exec(b | 0x8410, b | 0x8410, function()
    if not pending then return end
    pending, done = false, true
    local first, n, i = 0xFFFF, 0, 0
    while i * 2 < first do
      local w = rd(0x7F0000 + i * 2) | rd(0x7F0001 + i * 2) << 8
      if w ~= 0 then
        if w < first then first = w end
        w8(0x7F0000 + i * 2, off); w8(0x7F0001 + i * 2, off >> 8)
        n = n + 1
      end
      i = i + 1
    end
    L.log(string.format("TOPSTR %04X slots %d f%d", off, n, L.frame))
  end)
end
