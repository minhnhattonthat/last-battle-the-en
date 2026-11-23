-- Log each run of the battle LZ decoder (bank 30, window $7EC000; docs/re/battle.md): source [$70] and destination
-- ($73, bank $7E) the first time a new destination run starts. One line per (frame, dest high byte).
--   --script tools/lua/battle_lz.lua
local seen = {}
local function rd(a) return emu.read(a, emu.memType.snesMemory, false) end
for _, pc in ipairs({0x30F7B3, 0x30F7DA}) do
  L.on_exec(pc, pc, function()
    local s = emu.getState()
    local d = s["cpu.d"]
    local src = rd(d + 0x70) | (rd(d + 0x71) << 8) | (rd(d + 0x72) << 16)
    local dst = rd(d + 0x73) | (rd(d + 0x74) << 8)
    local key = L.frame * 256 + (dst >> 8)
    if seen[key] then return end
    seen[key] = true
    L.log(string.format("f%d BLZ src=%06X (off %06X) dst=7E%04X", L.frame, src, L.rom_off(src), dst))
  end)
end
