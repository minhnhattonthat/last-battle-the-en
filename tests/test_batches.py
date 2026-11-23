import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import batches  # noqa: E402


def hp(jp, en, id_="x"):
    return batches.honorific_problems({"id": id_}, jp, en)


def test_honorific_on_name_needs_suffix():
    assert hp("「リリヤちゃんを 助けて", '"Save little Lilja')
    assert not hp("「リリヤちゃんを 助けて", '"Save Lilja-chan')
    assert not hp("「ユ－リ様～！", '"Yuri-samaaa!')


def test_each_name_counts():
    jp = "「レジ－ナ様 リダ－ル様は？"
    assert hp(jp, '"Regina-sama, where is General Lidar?')
    assert not hp(jp, '"Regina-sama, where is Lidar-sama?')


def msg(id_, jp, en):
    e = {"id": id_, "jp": jp, "tiles": 11, "size": 40, "_file": "menus", "_kind": "bg3"}
    return batches.width_problems(e, en)


def test_name_inserts_count_at_their_longest():
    jp = " {FA18}を {FA42}に わたしました{009F}"
    # 1 + 5 + 9 (item) + 4 + 8 (character) + 1 = 28 > the 26-tile prompt box and the JP's 27
    assert msg("bg3_8E44", jp, " Gave {FA18} to {FA42}.")
    assert not msg("bg3_8E44", jp, "  Gave {FA42} {FA18}.")
    # outside the measured box the JP line (names at 8) is the limit
    assert msg("bg3_0000", "{FA18}を すてた", "Threw away {FA18}.")
    assert not msg("bg3_0000", "{FA18}を すてました", "{FA18} gone")  # 14 <= 15


def test_menu_prompt_centred_on_the_jp_in_its_box():
    def wrap(id_, jp, en, tiles):
        return batches.wrap({"id": id_, "jp": jp, "tiles": tiles, "size": 40, "_file": "menus", "_kind": "bg3"}, en)
    # JP centre 9 + 8/2 = 13; 13 - 13/2 = 6.5, rounded up: 7 spaces, past the JP string's own 17 tiles (26-tile box)
    assert wrap("bg3_8906", "         よろしいですか？", "Are you sure?", 17) == " " * 7 + "Are you sure?"
    # outside the box the JP string's tile count caps it; trailing JP blanks are not text
    assert wrap("bg3_985C", "  しゅうりょう する   ", "Done", 14) == " " * 5 + "Done"
    # a glyph token is a tile; a name counts at its longest on both sides
    assert wrap("bg3_8622", "   ステレオ／モノラルを えらんでください{009F}", "Choose stereo or mono.", 22) == \
        "  Choose stereo or mono."


def test_titles_and_non_names_are_exempt():
    assert not hp("城将グッベ様の命令だ", "Commander Gubbe's orders")
    assert not hp("枢機卿ケッテリ殿", "Cardinal Ketteri")
    assert not hp("オレ様に まかせろ", "Leave it to me")
    assert not hp("クルトさんは もう", "Kurt can't", "top15_03B6")
