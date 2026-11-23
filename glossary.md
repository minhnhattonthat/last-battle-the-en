# Glossary - The Last Battle (SNES, Teichiku 1994)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: a row's JP in a line needs one of its EN forms (`/` separates forms).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept (D1) where Japanese uses them on a name: 様 -> `-sama` (Yuri-sama), さん -> `-san`, くん -> `-kun`,
  ちゃん on a name -> `-chan`. Titles are English: 王 -> King, 王子 -> Prince, 姫 -> Princess, 兄ちゃん -> big brother.
  Name order: Western (given name first).
- Romanisation (D2): no official English names exist; names are Hepburn without macrons, read as the Scandinavian/German
  words the game borrows where the word is obvious (グルド = Guld, Swedish "gold"; ヴァテン = Vatten "water";
  リーケ = -rike "realm"; エット トヴォー トレー = "Ett, tva, tre", Swedish one-two-three).
- Credits: English (D3). Register: plain, warm storybook English; children and rough men keep their voice.
- Abbreviations: full words (D4). Item/spell names have an 8-tile field, so pick a short natural word first; a real
  abbreviation is flagged in the notes column.

## Style rules
- 「 opens speech -> `"`; the JP has no closing 」, and neither does the English (speech runs to the end of the box,
  continuation lines indented one space: the batch tool adds the indent and the line breaks).
- ・・・ -> `...`; ・・ -> `..`; ！！ -> `!!`; ？ -> `?`; ～ in a drawn-out word -> repeat the letter ("Hmmm").
- Write dialogue pages as running text; put `{page}` where the JP pages, or add one when a page passes 3 lines.
  `{wait}` may move inside the sentence; every other `{token}` must stay (names and numbers the game draws).
- No a/an right before `{item}`/`{spell}`/`{target}`: "found the {item}!", "used {item}".
- Plain ASCII only. No curly quotes, no em dashes (use `--` sparingly), no accents.
- Menu/BG3 strings: fixed 8 px tiles, the `limit` column is the hard tile count per line.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| クルト | Kurt | | hero, a boy from Eldar | Curt |
| メイ | Mei | | girl mage, Kurt's friend ("あたし") | May |
| ボルグ | Borg | | | |
| レジーナ | Regina | | | |
| コンラート | Konrad | | soldier, the boy's big brother | Conrad |
| ユーリ | Yuri | | Yuri-sama for ユーリ様 | Yuuri |
| フェーベンネルス | Febennels | | | |
| スヴァルト | Svart | | | |
| フェナムン | Fenamun | | | |
| スレーク | Sleek | | | |
| ビーボォ | Beebo | | | |
| イェルト | Yelt | | | |
| イスカール | Iskar | | | |
| ケッテリ | Ketteri | | also an enemy name | |
| ローグ | Rogue | | | |
| グスタフ | Gustav | | King Gustav (グスタフ王) | |
| グッベ | Gubbe | | | |
| ヒルダ | Hilda | | | |
| リリヤ | Lilja | | | |
| リダール | Lidar | | | |
| ロッタ | Lotta | | | |
| ラバン | Laban | | | |
| ルドム | Rudom | | | |
| エンティラン | Entiran | | | |
| デュケン | Duken | | | |
| カッテル | Kattel | | | |
| デュナス | Dunas | | | |
| トルン | Torn | | | |
| エルド | Eld | | | |
| ハイラム | Hiram | | | |
| ロベルト | Robert | | | |
| ガッキンコ | Gakkinko | | | |

## Places and peoples
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| グルド | Guld | | the enemy kingdom; グルド兵 = Guld soldier(s); never "Gold" | |
| グルドリーケ | Guldrike | | | |
| シルヴェル | Silvel | | Kurt's kingdom; シルヴェル城 = Silvel Castle | Silver |
| シルヴェルリーケ | Silvelrike | | | |
| エルダール | Eldar | | Kurt's village (エルダール村 = Eldar Village) | |
| ラントブルク / ラントブルグ | Landburg | | | |
| ベルクスタット | Bergstadt | | | |
| ハンスタッド / ハンスタット | Hanstad | | port town | |
| ハントヴォー | Hantvo | | western port | |
| ベルグデレン | Bergdelen | | fortress | |
| グルヴァ | Gulva | | village | |
| リッテン | Ritten | | village | |
| ウード | Ude | | kingdom | |
| ヤーク | Yaak | | ヤーク族 = the Yaak (tribe) | Yak |
| コッパス | Koppas | | raft people | |
| エルフ | elf / elves / elven | | case-insensitive check | |
| エント | Ent | | | |
| ノルドリグ | Nordrig | | | |
| クロケット | Kroket | | village | |
| エルディス | Eldis | | island of fire and ice | |
| ドキワ | Dokiwa | | cave | |
| ブレックフェール | Bleckfel | | | |
| キューケンホフ | Keukenhof | | | |

## Items / magic / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| マナ | mana / Mana | | 火/水/大地/風のマナ = Fire/Water/Earth/Wind Mana | |
| ネファ | Nepha | | | |
| オーラソード | Aura Sword | | | |
| ハーブ | herb / Herb | | | |

## Decisions from earlier batches
