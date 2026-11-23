-- Text coverage probe for The Last Battle (loaded after warp.lua; keys as in tools/strings_tsv.py).
--   TEXT <key> f<frame>: the game read a byte at that key (a string counts when its first byte is read).
--   ROM reads in RANGES ("lo-hi,lo-hi", CPU hex) log the file offset. Reads of $7F (decompressed script blocks)
--   log BLOCK_KEY | stream file offset << 16 | offset, the stream being the last decompression to $7F:0000
--   (00:83A7: source $AC-$AE, destination $B0-$B2, DP-relative; callers use D = $0000 or $0D00).
-- RUNS="0123,0456" (hex $7F addresses): after the warp's room is calm, run each as a script in turn (as the field
-- loop runs e1: $0634 = 1, then point the VM call 00:D64C at it), A tapped while it runs. Logs RUN/END per script,
-- LEFT when the room changes (its block is gone: the driver restarts after it), STUCK after MAXF frames, ALLDONE.
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function w8(a, v) emu.write(a, v & 0xFF, emu.memType.snesMemory) end
local function r16(a) return rd(a) | (rd(a + 1) << 8) end
local function w16(a, v) w8(a, v); w8(a + 1, v >> 8) end

local BLOCK_KEY = 1 << 40
local seen, cur = {}, nil
local function text(key)
  if seen[key] then return end
  seen[key] = true
  L.log(string.format("TEXT %X f%d", key, L.frame))
end
L.on_exec(0x0083A7, 0x0083A7, function()
  local dp = 0x7E0000 | emu.getState()["cpu.d"]  -- callers use DP $0000 or $0D00
  if rd(dp + 0xB2) == 0x7F and rd(dp + 0xB0) == 0 and rd(dp + 0xB1) == 0 then
    local src = rd(dp + 0xAC) | rd(dp + 0xAD) << 8 | rd(dp + 0xAE) << 16
    cur = L.rom_off(src)
    L.log(string.format("BLOCK %06X src %06X f%d", cur, src, L.frame))
  end
end)
L.on_read(0x7F0000, 0x7FFFFF, function(addr)
  if cur then text(BLOCK_KEY | cur << 16 | (addr & 0xFFFF)) end
end)
for lo, hi in string.gmatch(RANGES or "", "(%x+)-(%x+)") do
  L.on_read(tonumber(lo, 16), tonumber(hi, 16), function(addr) text(L.rom_off(addr)) end)
end

if not RUNS then return end
local runs = {}
for a in RUNS:gmatch("%x+") do runs[#runs + 1] = tonumber(a, 16) end
local MAXF = MAXF or 4000
local i, state, at, room = 0, "wait", 0, nil
local function stop(msg)
  L.log(msg); state = "done"; L.finish(0)
end
local function next_run()
  i = i + 1
  if i > #runs then stop("ALLDONE f" .. L.frame); return end
  w16(0x7E0634, 1)
  state, at = "armed", L.frame
end
L.on_exec(0x00D64C, 0x00D64C, function()
  if state ~= "armed" then return end
  w16(0x7E0C10, runs[i]); w16(0x7E0C12, 0x7F)
  state, at = "running", L.frame
  L.log(string.format("RUN %04X f%d", runs[i], L.frame))
end)
L.on_exec(0x00D634, 0x00D634, function()
  if state == "running" and L.frame > at + 1 then
    L.log(string.format("END %04X f%d", runs[i], L.frame))
    state, at = "gap", L.frame
  end
end)
local stable = 0
L.on_frame(function(n)
  if state == "done" then return end
  local calm = rd(0x7E00CC) == 0 and rd(0x7E00CE) == 0
  if state == "wait" then
    if calm and r16(0x7E002C) ~= 0 and L.route_done() then stable = stable + 1 else stable = 0 end
    if stable >= 180 then room = r16(0x7E002C); L.log("COVER room " .. room); next_run() end
    return
  end
  if r16(0x7E002C) ~= room or rd(0x7E00CE) ~= 0 then
    stop(string.format("LEFT %04X f%d", runs[i] or 0, n)); return
  end
  if state == "running" then
    -- A through the text; after 1500 frames B instead, to back out of shop or service menus that A keeps open
    if n % 12 == 0 then L.press(n - at > 1500 and "b" or "a", 2) end
    if n - at > MAXF then stop(string.format("STUCK %04X f%d", runs[i], n)) end
  elseif state == "armed" then
    -- a place-name label (rooms entered from the map) holds the field loop until a button closes it
    if (n - at) % 20 == 10 then L.press("b", 2) end
    if n - at > 400 then stop(string.format("NOSTART %04X f%d", runs[i], n)) end
  elseif state == "gap" and n - at > 30 and calm then
    next_run()
  end
end)
