# Glossary - The Last Battle (SNES, Teichiku 1994)

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the tables: a row's JP in a line needs one of its EN forms (`/` separates forms).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept (D1) where Japanese uses them on a name: 様 -> `-sama` (Yuri-sama), さん -> `-san`, くん -> `-kun`,
  ちゃん on a name -> `-chan`, 殿/どの on a name -> `-dono` (Yuri-dono, Kurt-dono). Titles are English and never take
  an honorific: 王 -> King, 王子 -> Prince, 姫 -> Princess, 兄ちゃん -> big brother, 枢機卿様 -> Your/His Eminence.
  Name order: Western (given name first).
- Romanisation (D2): no official English names exist; names are Hepburn without macrons, read as the Scandinavian/German
  words the game borrows where the word is obvious (グルド = Guld, Swedish "gold"; ヴァテン = Vatten "water";
  リーケ = -rike "realm"; エット トヴォー トレー = "Ett, tva, tre", Swedish one-two-three).
- Credits: English (D3). Register: plain, warm storybook English; children and rough men keep their voice.
- Abbreviations: full words (D4). Names fit their fields (D10): items and tactics 12 letters, spells 8, so pick a
  short natural word first; a real abbreviation is flagged in the notes column.

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
| メイ | Mei | | elf girl and mage ("あたし"), joins Kurt at Silvel Castle | May |
| ユース | Yuse | | Kurt's foster mother (Yelt's wife) | |
| ミアス | Mias | | Gustav's first queen, Kurt's real mother | |
| 王妃 | Queen | | Gustav's present queen (pregnant) | |
| グラッド | Glad | | Yuri's man, carries the Guld letter | |
| キューケンホフ先生 | Mr. Keukenhof | | Eldar schoolteacher (speaker label; "sir" when addressed) | |
| 長老 | Elder | | speaker label; "the Elder" in narration | |
| ボルグ | Borg | | | |
| レジーナ | Regina | | Princess Regina (レジーナ姫), hunted by Ketteri's men | |
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
| エルド | Eld | | Fenamun of fire (Swedish "eld") | |
| ヨルデン | Jorden | | Fenamun of earth | |
| ヴィンド | Vind | | Fenamun of wind | |
| ハイラム | Hiram | | | |
| ロベルト | Robert | | | |
| ガッキンコ | Gakkinko | | | |
| ファルク | Falk | | birdman elder | |
| ヘ－グ | Heeg | | Yaak, Rogue's friend in Bergstadt | |
| 破城つち | battering ram | | Yaak siege ram | |
| ライム | Lime | | elf queen (ライム王妃 = Queen Lime) | |
| ユルハ－タ | Yurhata | | Robert and Lime's daughter | |
| リ－ユ | Riyu / iruY | | Yuri's alias in the hidden village; iruY = "Yuri" in the backwards book r118_0115 | |
| ティラン | Tiran | | King Tiran of Guld, Regina's father | |

## Places and peoples
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| グルド | Guld | | the enemy kingdom; グルド兵 = Guld soldier(s); never "Gold" | |
| グルドリーケ | Guldrike | | | |
| シルヴェル | Silvel | | Kurt's kingdom; シルヴェル城 = Silvel Castle; シルバー (the metal) stays "Silver" | |
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
| ルドムの塔 | Tower of Rudom | | Febennels' training tower | |
| トルンの腕輪 / デュナスの腕輪 | Torn Bracelet / Dunas Bracelet | | dragon king's gifts, Silvel / Guld royal houses | |
| エンティラン川 | Entiran River | | "tyrant" | |
| ベ－テブルグ | Betteburg | | tall mountain (creation song) | |
| 真の言葉使い | true word-speaker | | elves who see the future through true words | |
| 星の広場 | Star Square | | clearing where the elf village appears | |
| ドキワ | Dokiwa | | cave | |
| ブレックフェール | Bleckfel | | | |
| キューケンホフ | Keukenhof | | | |

## Items / magic / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| マナ | mana / Mana | | 火/水/大地/風のマナ = Fire/Water/Earth/Wind Mana | |
| ネファ | Nepha | | 銀/金/光のネファ = Silver/Gold/Light Nepha | |
| ミランシェル | Miranchel | 12 | the finest armor (item_1D; 12-letter item name field, D10) | |
| オーラソード | Aura Sword | | | |
| ハーブ | herb / Herb | | | |
| ソル | Sol | | currency | |
| エットミランシェル | Ettmiranshel | | the world | |
| フェナムン | Fenamun | | a person's true name; フェナムンの儀式 = the Fenamun rite; フェナムンの宝珠 = Fenamun Orb | |
| 宰相 | Chancellor | | Chancellor Yuri-sama | |
| 枢機卿 | Cardinal | | Cardinal Ketteri; ケッテリ卿 = Lord Ketteri | |
| 城将 | Commander | | Commander Gubbe (castle commander) | |
| 第２グルド城 | Second Guld Castle | | occupied Silvel Castle | |
| 囚人島 | Prison Island | | | |
| 魔法合成 | spell synthesis | | magic healers' service | |
| 魔法司 | mage | | castle/town healer-mages | |
| 鳥人兵 | birdmen | | Guld flying troops | |
| いやしの館 | House of Healing | | | |
| 密書 | secret letter / Missive | | in talk "the secret letter"; the item and "received" messages: Guld Missive | |
| ヴァテン ブレックフェール レーカ | Vatten... Bleckfel... Reka! | | healing chant; エット トヴォー トレー = Ett, tva, tre! (fireball); Guld mage chant = Vem... Stor... Dod! | |
| ファイアボール / エクスプロード / ミラーイメージ / パラライズ | Fireball / Explode / Mirror / Paralyze | | spell names, 8 tiles | |
| トーネード / アイスストーム / プロテクション / リストアヘルス / ライトニング | Tornado / Icestorm / Protect / Restore / Thunder | | spell names, 8 tiles | |
| ヤーク族魔法司 / 族長の娘 / グルド隊長 | Yaak Mage / Chief's Daughter / Guld Captain | | speaker labels | |

## Decisions from earlier batches
- Speaker pages are `Name{nl}"speech` (b006): the name line is one of the box's 3 lines; the batch tool wraps the
  speech and keeps the name line.
- Shop templates `{actor}さん` drop the honorific (b014-b016): "{actor}, what'll you buy?", not "{actor}-san".
- Riyu / iruY (b026): Yuri's alias is "Riyu"; in the backwards book (r118_0115) the name is spelled "iruY" so the
  reversed reading still gives "Yuri".
- Titles never carry an honorific (phase-6 review): 枢機卿様 -> "Your Eminence" / "His Eminence".
- Beebo calls Febennels フェーベン様 = "Feben-sama"; her cry is "Kee kee!" (phase-6 review).
- Old-man and quirk speech (ぞい, じゃ, ギ, pidgin) keeps an English device per `docs/style-reference.md` (phase-6
  review: a flattened voice is Important).
