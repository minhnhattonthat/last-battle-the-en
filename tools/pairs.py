"""Reviewer pairs files: one per batch, entries in script order, `>> id | JP` then `   EN`, with two context entries
before and after the batch (marked `ctx`). Box breaks are folded: JP {nl} removed, EN {nl} -> space, {page} -> ` / `.

    python -X utf8 tools/pairs.py [bNNN ...]     -> work/review/bNNN.txt (default: every work/tl/bNNN.tsv)

Read each file with offset/limit (the context-mode hook stubs reads over ~4 KB). Verdicts: docs/review-phase6.md.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
TL = os.path.join(ROOT, 'work', 'tl')
OUT = os.path.join(ROOT, 'work', 'review')


def fold(s, jp):
    s = s.replace('{nl}', '' if jp else ' ')
    s = re.sub(r'\{page2?\}', ' / ', s)
    s = re.sub(r'\{(wait|FB00)\}', '', s)
    return re.sub(r'  +', ' ', s).strip()


def script():
    order, by_id = [], {}
    for path in sorted(glob.glob(os.path.join(ROOT, 'script', '*.json'))):
        for e in json.load(open(path, encoding='utf-8'))['entries']:
            order.append(e['id'])
            by_id[e['id']] = e
    return order, by_id


def main(argv):
    os.makedirs(OUT, exist_ok=True)
    names = argv or sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(TL, 'b[0-9][0-9][0-9].tsv')))
    order, by_id = script()
    pos = {i: n for n, i in enumerate(order)}
    for name in names:
        ids = [l.split('\t', 1)[0] for l in open(os.path.join(TL, name + '.tsv'), encoding='utf-8').read().split('\n') if l]
        ids = sorted((i for i in ids if i in pos), key=pos.get)
        if not ids:
            continue
        first, last = pos[ids[0]], pos[ids[-1]]
        ctx_before = order[max(0, first - 2):first]
        ctx_after = order[last + 1:last + 3]
        lines = []
        for i in ctx_before + ids + ctx_after:
            e = by_id[i]
            tag = 'ctx ' if i in ctx_before or i in ctx_after else ''
            lines.append(f">> {tag}{i} | {fold(e['jp'], True)}")
            lines.append(f"   {fold(e.get('en') or '(untranslated)', False)}")
        with open(os.path.join(OUT, name + '.txt'), 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
        print(name, len(ids), 'entries', sum(len(l) for l in lines), 'chars')


if __name__ == '__main__':
    main(sys.argv[1:])
