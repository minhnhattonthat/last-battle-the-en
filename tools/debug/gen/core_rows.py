T = "\t"
mash = lambda n: ";".join(["6 a;14 -"] * n)
rows = [
    ("newgame", "-", "-", "-", "-", "-", "-", "60 -", "first room as a new game starts it (room 2, Kurt's house; intro script)"),
    ("overworld", "0x00", "40", "30", "2", "noenc", "-", "60 -", "overworld (mode 7), next to land"),
    ("menu_cmd", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;60 -", "field command menu (A): どうしますか? + 8 icons"),
    ("menu_search", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 a;120 -", "search: nobody here"),
    ("menu_magic", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "magic"),
    ("menu_item", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "items"),
    ("menu_equip", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "equipment"),
    ("menu_status", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 right;40 -;6 a;90 -;6 a;120 -", "status"),
    ("menu_system", "0x4D", "10", "6", "2", "-", "-", "60 -;6 a;40 -;6 left;40 -;6 a;90 -", "system: stereo/mono only"),
    ("battle_field", "0x00", "40", "30", "2", "god,@1DDF:0053", "-", "300 -;" + mash(40), "random-encounter group $53 on the overworld; commands and messages"),
    ("battle_room", "0x4D", "10", "6", "2", "god,@1DDF:002B", "-", "300 -;" + mash(40), "encounter group $2B forced inside a house"),
    ("battle_win", "0x00", "40", "30", "2", "god,win,@1DDF:0053", "-", "300 -;" + mash(330), "victory, experience, LEVEL UP!! window"),
    ("wipeout", "0x00", "40", "30", "2", "@1DDF:0053", "-", "300 -;" + mash(70), "party wiped out: 全滅しました・・・ then back to the title (no separate game-over screen)"),
]
for r in rows:
    assert len(r) == 9
    print(T.join(r))
