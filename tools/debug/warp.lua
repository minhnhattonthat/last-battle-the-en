-- Debug warp for The Last Battle (SNES). Cold boot -> any scene in tools/debug/scenes.tsv, no save needed.
--
--   python -X utf8 $SKILL/scripts/emu.py build/lastbattle_en.sfc --out work/qa/warp --script tools/debug/warp.lua
--          --var "SCENE='<name>'" --frames 3600 --sheet [--var GOD=1] [--var NOENC=1] [--var FAST=1]
--
-- How it works (docs/re/debug.md):
--  * Boot: Start x3 through logo/title, then A mashed through name entry until the new-game script asks for the
--    first room. The map-change request lives at $7E0D22-$0D2B (script op BA writes it: $0D24 room id 1-based,
--    $0D26 x, $0D28 y, $0D2A facing); 00:964C prepares the room (loads its script block via 01:E631), 00:9679
--    switches. warp.lua overwrites the request at 00:964C on the first call, so the game itself loads the scene.
--  * Scene columns (tab separated, '-' = none):
--      name  room  x  y  dir  pokes  run  keys  notes
--    pokes: "ADDR=VAL,ADDR=VAL" (hex, 8-bit, written when the room is prepared; ADDR may be a 24-bit WRAM address);
--           a "ADDR:VAL" pair is instead 16-bit; a leading "@" writes it at READY instead ("@1DDF:0053" = battle
--           with encounter group $53: the field loop starts a battle when $1DDF != $FFFF); the words god, win,
--           noenc in the list turn those cheats on for the scene.
--    run:   script address in the room block image ($7F:xxxx) run instead of the room's entry script (e0):
--           NPC talks, events; or "ops:<hex bytes>" = raw script bytes run from $7EFF00 (FF00 appended), e.g.
--           "ops:06E400" = op E406 arg 00 (healer): shops, inns, battles.
--    keys:  presses after the scene is ready, route syntax with ';' between steps ("40 -;6 x;60 -").
--  * Ready = the field loop is running with no fade or request pending (scene flag logged "READY f<frame>").
--  * GOD=1 refills party HP every frame; NOENC=1 zeroes the encounter counter; both optional.
-- scenes.tsv: SCENES_FILE if given, else walk up from the --out dir to the repo's tools/debug/scenes.tsv.
local function find_scenes()
  if SCENES_FILE then return SCENES_FILE end
  local dir = OUT:gsub("\\", "/"):gsub("/$", "")
  while dir:find("/") do
    local p = dir .. "/tools/debug/scenes.tsv"
    local f = io.open(p, "r")
    if f then f:close(); return p end
    dir = dir:match("^(.*)/[^/]*$")
  end
  error("tools/debug/scenes.tsv not found above " .. OUT .. "; pass --var \"SCENES_FILE='C:/.../scenes.tsv'\"")
end
local SCENES = find_scenes()

local STUB = 0x7EFF00   -- free WRAM (zero in every dump checked) for injected script bytes
local function rd(a) return emu.read(a, emu.memType.snesMemory) end
local function w8(a, v) emu.write(a, v & 0xFF, emu.memType.snesMemory) end
local function w16(a, v) w8(a, v); w8(a + 1, v >> 8) end
local function r16(a) return rd(a) | (rd(a + 1) << 8) end

local function split(s, sep)
  local t = {}
  for f in (s .. sep):gmatch("(.-)" .. sep) do t[#t + 1] = f end
  return t
end
local function num(s) if s == nil or s == "-" or s == "" then return nil end return tonumber(s) end

local scene
-- Ad-hoc probe without a scenes.tsv row: --var ROOM=0x4D --var X=10 --var Y=6 [--var DIR=2] [--var RUN=0x0123]
--   [--var "KEYS='60 -;6 a'"] [--var "OPS='06E400'"] [--var "POKES='0200=1'"]
if ROOM then
  SCENE = "adhoc"
  scene = { name = SCENE, room = ROOM, x = X, y = Y, dir = DIR or 2, pokes = POKES or "-", keys = KEYS or "-",
            ops = OPS, run = RUN }  -- RUN: $7F address run instead of the room's entry script
end
for line in io.lines(SCENES) do
  if not (scene and scene.name == "adhoc") and line:sub(1, 1) ~= "#" and line:match("%S") then
    local c = split(line, "\t")
    if c[1] == SCENE then
      scene = { name = c[1], room = num(c[2]), x = num(c[3]), y = num(c[4]), dir = num(c[5]) or 2,
                pokes = c[6] or "-", keys = c[8] or "-", mode = (c[2] == "title" or c[2] == "load") and c[2] }
      local run = c[7] or "-"
      if run:match("^ops:") then scene.ops = run:sub(5):gsub("%s", "") else scene.run = num(run) end
    end
  end
end
if not scene then error("scene not in " .. SCENES .. ": " .. tostring(SCENE)) end
L.log("SCENE " .. scene.name)
-- flag words in the pokes column turn the cheats on per scene: god, win, noenc
local rest = {}
for p in scene.pokes:gmatch("[^,]+") do
  local w = p:lower():match("^%s*(%a+)%s*$")
  if w == "god" then GOD = 1 elseif w == "win" then WIN = 1 elseif w == "noenc" then NOENC = 1
  elseif w == "credits" then CREDITS = 1
  elseif p:match("^%s*sav=") then -- battery save for run_scenes.py (--sav work/saves/<file>); nothing to do here
  elseif p ~= "-" then rest[#rest + 1] = p end
end
scene.pokes = #rest > 0 and table.concat(rest, ",") or "-"
scene.battle = scene.pokes:upper():find("1DDF") ~= nil

local function apply_pokes(late)
  if scene.pokes == "-" then return end
  for p in scene.pokes:gmatch("[^,]+") do
    local at, a, sep, v = p:match("^%s*(@?)(%x+)([=:])(%x+)%s*$")
    if not a then error("bad poke: " .. p) end
    if (at == "@") ~= late then goto continue end
    a = tonumber(a, 16); v = tonumber(v, 16)
    if a < 0x10000 then a = 0x7E0000 + a end
    if sep == ":" then w16(a, v) else w8(a, v) end
    ::continue::
  end
end

-- Boot: Start through logo/title/menu, then mash A through name entry (stops once the room is requested).
-- room "title": no boot at all, the keys run from power-on (title, LOAD screen with a save). room "load": the
-- same boot, but with a save present the title's default is LOAD, so the third Start opens the load screen and
-- the A taps load FILE1; the room is the saved one (not overwritten).
local phase = "boot"
if scene.mode == "title" then
  phase = "ready"
  L.log("READY f0 title")
  for step in scene.keys:gmatch("[^;]+") do
    local f, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    if not f then error("bad keys step: " .. step) end
    L.press(spec, tonumber(f))
  end
else
  L.press("-", 600); L.press("start", 6); L.press("-", 300); L.press("start", 6); L.press("-", 300)
  L.press("start", 6); L.press("-", 600)
end
L.on_frame(function(n)
  if phase == "boot" and L.route_done() and n % 20 < 6 then
    -- name entry: tap A (queued per frame so the harness MASH is not needed)
    L.press("a", 1)
  end
end)

local prepared = false
L.on_exec(0x00964C, 0x00964C, function()
  if prepared then return end
  prepared = true
  phase = "load"
  if scene.room then
    w16(0x7E0D24, scene.room)
    if scene.x then w16(0x7E0D26, scene.x) end
    if scene.y then w16(0x7E0D28, scene.y) end
    w16(0x7E0D2A, scene.dir)
  end
  apply_pokes(false)
  L.log(string.format("PREP f%d room=%d x=%d y=%d dir=%d", L.frame, r16(0x7E0D24), r16(0x7E0D26), r16(0x7E0D28),
    r16(0x7E0D2A)))
end)

-- Entry script of the new room (00:D656 -> $7F0000 word -> $0C10): replace it with RUN if given.
local ran = false
L.on_exec(0x00D666, 0x00D666, function()
  if ran or not prepared then return end
  ran = true
  if scene.run then
    w16(0x7E0C10, scene.run); w16(0x7E0C12, 0x7F)
    L.log(string.format("RUN f%d $7F:%04X", L.frame, scene.run))
  end
end)

-- ops: once the field runs (READY), write the bytes at STUB (+ FF00 end) and set $0634, which makes the field
-- loop run the room's e1 script (00:D634: $7F0002 -> $0C10, VM call at 00:D64C); the hook at D64C points the
-- VM at STUB instead. The room is set up and faded in, as when an NPC script runs.
local ops_armed = false
local function arm_ops()
  local a = STUB
  for i = 1, #scene.ops, 2 do w8(a, tonumber(scene.ops:sub(i, i + 1), 16)); a = a + 1 end
  w8(a, 0x00); w8(a + 1, 0xFF)
  w16(0x7E0634, 1)
  ops_armed = true
end
L.on_exec(0x00D64C, 0x00D64C, function()
  if not ops_armed then return end
  ops_armed = false
  w16(0x7E0C10, STUB & 0xFFFF); w16(0x7E0C12, STUB >> 16)
  L.log(string.format("OPS f%d %s at $%06X", L.frame, scene.ops, STUB))
end)

-- CREDITS: the ending (op A404 -> 02:D598) first shows the epilogue and "Fin" (02:D988), which waits on the sound
-- CPU (02:DB40, $2143 bit 1) and never moved on in 110000 frames from a warp; skip that call so the staff roll
-- (02:D618, 02:D6DA, text 0x16245) plays.
if CREDITS then
  L.on_exec(0x02D5BE, 0x02D5BE, function()
    local s = emu.getState()
    s["cpu.pc"] = 0xD5C1
    emu.setState(s)
    L.log("CREDITS skip 02:D988 f" .. L.frame)
  end)
end

-- GOD: HP and MP to max every frame for every party slot (records $7E1900 + slot*$E4: HP $09, max $0B, MP $0D,
-- max $0F; party size $7E003E). NOENC: cancel any random encounter ($7E1DDF back to $FFFF) after READY; a forced
-- "@1DDF" poke is written after this hook has run, so it still starts its battle.
L.on_frame(function(n)
  if GOD then
    for slot = 0, 3 do
      local b = 0x7E1900 + slot * 0xE4
      local mhp = r16(b + 0x0B)
      if mhp > 0 and mhp < 10000 then w16(b + 0x09, mhp); w16(b + 0x0D, r16(b + 0x0F)) end
    end
    -- in battle ($1DDF holds the group) the party units are copies at $7E1298 + i*$28 (29:B216): HP +$0E,
    -- max +$10, MP +$12, max +$14. A refill at frame end loses to a killing blow inside the frame, so the
    -- battle copies get 999 HP (max too); the field records are untouched.
    if r16(0x7E1DDF) ~= 0xFFFF then
      for i = 0, 3 do
        local b = 0x7E1298 + i * 0x28
        local mhp = r16(b + 0x10)
        if mhp > 0 and mhp < 10000 then w16(b + 0x10, 999); w16(b + 0x0E, 999); w16(b + 0x12, r16(b + 0x14)) end
      end
    end
  end
  -- WIN: the party's battle copies of the record's first three stat words (+$16/+$18/+$1A, from record +0/+2/+4,
  -- 29:B22A) go to 999, so the party wins and the victory, experience and level-up messages show.
  if WIN and r16(0x7E1DDF) ~= 0xFFFF then
    for i = 0, 3 do
      local b = 0x7E1298 + i * 0x28
      if r16(b + 0x10) > 0 then w16(b + 0x16, 999); w16(b + 0x18, 999); w16(b + 0x1A, 999) end
    end
  end
  if NOENC and phase == "ready" and not scene.battle then
    if r16(0x7E1DDF) ~= 0xFFFF then w16(0x7E1DDF, 0xFFFF) end
  end
end)

-- Ready: room loaded, no fade ($CC), no change request ($CE). Then queue the scene's keys.
local ready_at, prep_frame
L.on_frame(function(n)
  if phase == "load" then prep_frame = prep_frame or n end
  local target = scene.room or 2
  local entered = r16(0x7E002C) == target and (ran or target == 0)
  if scene.mode == "load" then entered = ran or r16(0x7E002C) == 0 end
  if phase == "load" and n - prep_frame > 60 and entered and rd(0x7E00CC) == 0 and rd(0x7E00CE) == 0 then
    ready_at = ready_at or n
    if n - ready_at >= 60 then
      phase = "ready"
      L.log("READY f" .. n .. " room " .. r16(0x7E002C))
      if scene.ops then arm_ops() end
      apply_pokes(true)
      if scene.keys ~= "-" then
        for step in scene.keys:gmatch("[^;]+") do
          local f, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
          if not f then error("bad keys step: " .. step) end
          L.press(spec, tonumber(f))
        end
      end
    end
  end
  if phase == "ready" and L.route_done() and not scene.done then
    scene.done = true
    L.log("KEYS DONE f" .. n)
  end
end)
