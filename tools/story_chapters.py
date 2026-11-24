"""Write one story-pass file per chapter into work/qa/story/chapters/ (phase 9, skill translation.md §Review).

Chapters are the room ranges of docs/synopsis.md. Each line: `>> id | speaker | JP` then `EN`, in room/script order.
The speaker is the name line before the first {nl} when the entry opens with one (e.g. `Beebo{nl}"...`), else '-'.
Usage: python -X utf8 tools/story_chapters.py [--out work/qa/story/chapters]
"""
import argparse, json, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CHAPTERS = [
    ('ch1_eldar', 0, 10), ('ch2_silvel_falls', 11, 45), ('ch3_rudom', 46, 100),
    ('ch4_hidden_village', 101, 160), ('ch5_retaking_silvel', 161, 200), ('ch6_guld', 201, 265),
    ('ch7_last_battle', 266, 322),
]


def speaker(en):
    head = en.split('{nl}', 1)[0] if en else ''
    if '{nl}' in (en or '') and head and not head.startswith(('"', "'", '(', '.')) and len(head) <= 24 \
            and re.fullmatch(r"[A-Z][\w .'-]*", head):
        return head
    return '-'


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--out', default=os.path.join(ROOT, 'work', 'qa', 'story', 'chapters'))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for name, lo, hi in CHAPTERS:
        lines = []
        for r in range(lo, hi + 1):
            p = os.path.join(ROOT, 'script', 'r%03d.json' % r)
            if not os.path.exists(p):
                continue
            d = json.load(open(p, encoding='utf-8'))
            for e in d.get('entries', []):
                en = e.get('en') or ''
                lines.append('>> %s | %s | %s\n%s\n' % (e['id'], speaker(en), e['jp'], en))
        with open(os.path.join(a.out, name + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines))
        print(name, len(lines), 'entries')


if __name__ == '__main__':
    main()
