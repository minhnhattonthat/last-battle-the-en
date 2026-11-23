T = "\t"
mash = lambda n: ";".join(["6 a;14 -"] * n)
rows = [
    ("newgame", "-", "-", "-", "-", "-", "-", "60 -", "first room as a new game starts it (room 2, Kurt's house; intro script)"),
    ("overworld", "0x00", "40", "30", "2", "noenc", "-", "60 -", "overworld (mode 7), next to land"),
    ("menu_cmd", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;60 -", "field command menu (A): どうしますか? + 7 icons (talk search magic item status tactics system)"),
    ("menu_search", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 a;120 -", "search: nobody here"),
    ("menu_magic", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "magic"),
    ("menu_item", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "items"),
    ("menu_status", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "status screen: stats, equipment slots, money"),
    ("menu_tactics", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "tactics: さくせんを えらぶ, 4 tactic icons"),
    ("menu_formation", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 right;60 -;6 a;150 -", "tactics > formation (たいれつ): だれの いちを へんこう しますか?"),
    ("menu_system", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 left;40 -;6 a;90 -", "system: stereo/mono only"),
    ("ow_menu", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -", "overworld menu (A): 5 icons (magic item status tactics camp); the first A after READY is ignored, hence the 300"),
    ("camp_menu", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -", "overworld camp icon: セーブする / ゲームをおわる"),
    ("save_files", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -;6 a;200 -", "save: どのファイルに セーブしますか? FILE1/FILE2 (NEW FILE)"),
    ("save_confirm", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -;6 a;200 -;6 a;200 -", "save: よろしいですか? はい/いいえ"),
    ("save_done", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -;6 a;200 -;6 a;200 -;6 a;200 -;6 a;200 -", "save written to FILE1 (make_saves.py copies this run's .srm to work/saves/base_file1.srm)"),
    ("quit_prompt", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -;6 right;60 -;6 a;300 -", "camp > ゲームをおわる: セーブしますか?"),
    ("quit_nosave", "0x00", "40", "30", "2", "noenc", "-", "300 -;6 a;300 -;6 left;60 -;6 a;200 -;6 right;60 -;6 a;300 -;6 right;60 -;6 a;600 -", "quit without saving: back to the title"),
    ("title", "title", "-", "-", "-", "-", "-", "600 -;6 start;300 -", "title menu with no save: NEWGAME only (logo, ©1994 TEICHIKU)"),
    ("name_entry", "title", "-", "-", "-", "-", "-", "600 -;6 start;300 -;6 start;300 -;6 start;600 -", "new game: name entry screen"),
    ("title_load", "title", "-", "-", "-", "sav=base_file1.srm", "-", "600 -;6 start;300 -;6 start;300 -;6 start;300 -", "title with a save: NEWGAME/LOAD (LOAD is the default), then the load screen (FILE1 name and level)"),
    ("load_file1", "load", "-", "-", "-", "sav=base_file1.srm", "-", "60 -", "load FILE1 from the title: the saved place (overworld 40,30)"),
    ("stress_money", "load", "-", "-", "-", "sav=stress_money.srm", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "save.py: money 9999999, loaded in room 77; status screen shows the 7-digit money"),
    ("battle_field", "0x00", "40", "30", "2", "god,@1DDF:0053", "-", "300 -;" + mash(40), "random-encounter group $53 on the overworld; commands and messages"),
    ("battle_room", "0x4D", "10", "6", "2", "god,@1DDF:002B", "-", "300 -;" + mash(40), "encounter group $2B forced inside a house"),
    ("battle_win", "0x00", "40", "30", "2", "god,win,@1DDF:0053", "-", "300 -;" + mash(330), "victory, experience, LEVEL UP!! window"),
    ("wipeout", "0x00", "40", "30", "2", "@1DDF:0053", "-", "300 -;" + mash(70), "party wiped out: 全滅しました・・・ then back to the title (no separate game-over screen)"),
]
# Story variants of rooms (00:B305): $EC|$EE = k (1-10) loads block 28+k for room VARIANT_EC[k-1] instead of its
# normal block; story flag $026F loads blocks 39-42 for rooms 1, $1A, $88, $F8 (block 39 = room 1 = the ending).
VARIANT_EC = [0x01, 0x15, 0x78, 0x89, 0xB9, 0x107, 0xDB, 0x10C, 0x110, 0xF8]
for k, room in enumerate(VARIANT_EC, 1):
    rows.append((f"variant_ec{k:02d}", f"0x{room:02X}", "10", "8", "2", f"god,EC={k:02X}", "-", "60 -;" + mash(200),
                 f"room {room} story variant: block {28 + k} ($EC={k}), events mashed with A"))
for i, room in enumerate([0x1A, 0x88, 0xF8], 1):
    rows.append((f"variant_6f_{room:02X}", f"0x{room:02X}", "10", "8", "2", "god,026F=01", "-", "60 -;" + mash(200),
                 f"room {room} late variant: block {39 + i} (flag $026F)"))
rows += [
    ("ending", "0x01", "10", "8", "2", "god,026F=01", "-", "60 -;" + mash(600),
     "ending: room 1 + story flag $026F (block 39): epilogue events, op A404, epilogue text and Fin (02:D988)"),
    ("credits", "0x01", "10", "8", "2", "god,credits,026F=01", "-", "60 -;" + mash(1300),
     "staff roll (02:D6DA, 24 entries, text 0x16245); the credits cheat skips Fin's endless wait on the sound CPU"),
]
for r in rows:
    assert len(r) == 9
    print(T.join(r))
