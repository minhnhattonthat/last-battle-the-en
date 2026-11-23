-- Log each decompression call into WRAM: when the LZ routine (00:8417 byte reader, ptr in DP $00-$02 with D=$0100)
-- first reads a new source run, log source pointer and destination ([$04], DP $04-$06). One line per new dest.
local seen = {}
local function rd(a) return emu.read(a, emu.memType.snesMemory, false) end
L.on_exec(0x008417, 0x008417, function()
  local s = emu.getState()
  local d = s["cpu.d"]
  local src = rd(d) | (rd(d + 1) << 8) | (rd(d + 2) << 16)
  local dst = rd(d + 4) | (rd(d + 5) << 8) | (rd(d + 6) << 16)
  local key = string.format("%06X", dst & 0xFFFF00)
  if not seen[key] and (dst & 0xFF) == 0 then
    seen[key] = true
    L.log(string.format("f%d src=%06X (off %06X) dst=%06X D=%04X", L.frame, src, L.rom_off(src), dst, d))
  end
end)
