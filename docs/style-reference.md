# Style reference

What translators, fixers and reviewers match. Binding names: `glossary.md`. Rulings: `docs/decisions.md`.
Rewritten in session 16 after the phase-6 review: every voice row names the JP markers and the English devices that
carry them. A row that only says "old-fashioned" is not enough; reviewers rate a flattened marker Important.

## Format
- Speaker pages `Name{nl}"speech`; `"` opens speech and never closes; a continuation page starts with one space.
- Plain ASCII, no em dashes; `...` for JP `・・・`; `!?` kept as written; `{wait}` codes stay where the JP has them.
- Honorifics (D1): on names only, as the JP has them: `様` -> `-sama`, `殿/どの` -> `-dono`, `さん` -> `-san`.
  Titles are English and never take one: 枢機卿様 -> "Your Eminence" (address) / "His Eminence" (reference),
  グスタフ王 -> "King Gustav", 長老 -> "Elder". `{actor}さん` in shop templates drops it.
- Narration (books, scene captions): past tense throughout a page set.

## Voices

| Speaker | JP markers | English devices |
|---|---|---|
| **Yaak Chief** (ヤ－ク族長) | ぞい / ぞい？ sentence ends, わし/ワシ, ヌシ(ら), じゃ, オホン, しょうぞい | gruff, boastful old chief. A tag on most lines: "eh?" on questions and asides, "mark me" or "hoh!" on boasts; dropped g's and "'em" ("nothin'", "carryin'"), "you lot" for ヌシら, "this old Yaak" for わし when he brags. Keep one tag per page at most |
| **Febennels** (フェ－ベンネルス) | じゃ, のじゃ, じゃろう, よかろう, わし, おまえ | old wizard: formal, unhurried, few contractions in his own statements, archaic touches ("Very well", "mustn't dawdle", "listen well"), "my boy" to Kurt now and then, "Hmm" for ふむ |
| **Elders** (長老, castle elders, old villagers) | じゃ, しとる, じゃと, わし, のう | old-timer: "eh?", "now, now", "what's this?", "my boy/lad", "I'd wager"; never neutral-modern |
| **Koppas Elder** (コッパス長老) | ギ at every clause end, ～ | ", gi" at clause ends; "~" kept as written |
| **Birdmen, Yaak pidgin** (鳥人) | katakana-heavy, particles dropped (ワレワレ, カエル) | broken English: dropped articles and verb endings ("We sorry", "We walk home on feet") |
| **Beebo** (ビ－ボォ) | キキッ/キ－ cries, わよ/なんだから, フェ－ベン様 | chatty, cheeky; cry spelled "Kee kee!"; calls Febennels "Feben-sama" (her short form) |
| **Mei** (メイ) | あたし, でしょ, のよ/だわ, こいつ | quick, blunt with Kurt ("this guy", "isn't it?"), girlish tags ("you know") |
| **Regina** (レジ－ナ) | だ/のか, おまえ(たち), 私 | princess-warrior: clipped commands, no softeners ("Silence!", "Who are you?") |
| **Borg, Yaak fighters, sailors, thugs** | おれ, ちっ, ふんっ, だぜ/だろ | rough contractions ("gonna", "Tch!", "Hmph", "Curses!") |
| **Yuri, Svart, officers** | 私, だね/だ, ください | measured adult authority; Guld officers formal and stiff ("You are a traitor against our Guld kingdom") |
| **Yelt** (イェルト) | だぞ, んだ | warm big-brother: plain, encouraging ("don't you be afraid") |
| **Kings** (グスタフ王, ロベルト王) | 私は ... だ, のだ | formal, no contractions ("I am Robert, king of the elves.") |
| **Shopkeepers** | top14 casual, top15 servile ございます | "What'll you buy?" / "A customer of taste!" |
| **Chants** | katakana nonsense | romanised Swedish-flavoured, dotted pauses ("Vatten... Bleckfel... Reka!") |

## Paired examples

- Febennels, `r000_0AA4`: 「おお クルト！ よくぞ やりとげた！！ これで儀式は終わりじゃ。」 -> "Oh, Kurt! You have done it!! This
  brings the rite to its end."
- Elder, `r000_11EE`: 「どうも ただのケガ人では なさそうじゃ。」 -> "This looks like no ordinary injury."
- Koppas Elder, `r174_0383`: 「待つギ～！！ 悪かったギ あやまるギ」 -> "Wait, gi~!! I was wrong, gi, I'm sorry, gi."
- Birdman, `r135_1434`: 「ワシら はんせいした。 島まで アシで 歩いてカエル。」 -> "We sorry. We walk home on feet to island."
- Beebo, `r076_134A`: 「キキッ キ－！ ただの リスじゃないわよ。 これでもフェ－ベン様の 一番弟子なんだから！」 -> "Kee kee! I'm no
  ordinary squirrel. I'm Feben-sama's top pupil, you know!"
- Regina, `r075_01FE`: 「だまれ！ ケッテリのイヌども！」 -> "Silence, you dogs of Ketteri!"

### Corrected example (Yaak Chief, `r138_0710`)
JP: 「こう見えても むかしは 傭兵隊長まで つとめたワシぞい。 そのころの ワシに 壊せんものは なかったぞい。 この ワシから見れば
スヴァルトも まだ まだ ただの ガキぞい。」
- Before (flattened): "I may not look it, but in my day I was a mercenary captain. / Back then, there was nothing I
  couldn't smash. / To me, even Svart is still just a kid."
- After: "Hoh, I may not look it, but this old Yaak was a mercenary captain once! / Back then there was nothin' I
  couldn't smash, mark me. / Next to me, even Svart's still just a whelp, eh?"

## Names
Spells 8 letters, items up to 9, tactics 8 (D18); currency "Sol".
