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


def test_titles_and_non_names_are_exempt():
    assert not hp("城将グッベ様の命令だ", "Commander Gubbe's orders")
    assert not hp("枢機卿ケッテリ殿", "Cardinal Ketteri")
    assert not hp("オレ様に まかせろ", "Leave it to me")
    assert not hp("クルトさんは もう", "Kurt can't", "top15_03B6")
