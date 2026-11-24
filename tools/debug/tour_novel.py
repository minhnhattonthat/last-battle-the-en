"""Which frames of a re-shot tour scene show something no earlier tour of it showed.

    python -X utf8 tools/debug/tour_novel.py NEW_TOUR OLD_TOUR [OLD_TOUR..] --out DIR [--only a,b] [--min 150]

For each scene dir in NEW_TOUR: every f*.png whose pixels match no frame of the same scene in any OLD_TOUR is
compared with the old frames near the same position (+-6 in the sorted list: re-shots drift by a few frames); if even
the nearest one differs in >= --min pixels, the frame counts as novel. Writes DIR/<scene>.png (old | new crops of the
distinct novel regions, 2x) and prints one line per scene: novel frames / regions. Used to decide whether a tour sheet
that changed only by timing needs a fresh visual-QA read (session 32).
"""
import argparse
import glob
import hashlib
import os

import numpy as np
from PIL import Image, ImageDraw


def load(p):
    return np.asarray(Image.open(p).convert('RGB'), dtype=np.int16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('new')
    ap.add_argument('old', nargs='+')
    ap.add_argument('--out', required=True)
    ap.add_argument('--only')
    ap.add_argument('--min', type=int, default=150)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    scenes = sorted(d for d in os.listdir(a.new) if os.path.isdir(os.path.join(a.new, d)))
    if a.only:
        keep = set(a.only.split(','))
        scenes = [s for s in scenes if s in keep]
    for s in scenes:
        news = sorted(glob.glob(os.path.join(a.new, s, 'f*.png')))
        olds = []
        for t in a.old:
            olds += sorted(glob.glob(os.path.join(t, s, 'f*.png')))
        if not olds:
            print(f'{s}\tNO-OLD\t{len(news)} frames')
            continue
        oldh = {}
        for p in olds:
            oldh.setdefault(hashlib.sha1(load(p).tobytes()).hexdigest(), p)
        # position index per old tour, by file name
        names = sorted({os.path.basename(p) for p in olds})
        crops, seen, novel = [], set(), 0
        for i, p in enumerate(news):
            img = load(p)
            if hashlib.sha1(img.tobytes()).hexdigest() in oldh:
                continue
            name = os.path.basename(p)
            j = names.index(name) if name in names else min(i, len(names) - 1)
            cand = []
            for t in a.old:
                for n in names[max(0, j - 6): j + 7]:
                    q = os.path.join(t, s, n)
                    if os.path.exists(q):
                        cand.append(q)
            best, bq = None, None
            for q in cand:
                o = load(q)
                if o.shape != img.shape:
                    continue
                m = np.abs(o - img).sum(-1) > 30
                if best is None or m.sum() < best.sum():
                    best, bq = m, q
            if best is None or best.sum() < a.min:
                continue
            novel += 1
            ys, xs = np.nonzero(best)
            box = (max(0, xs.min() - 8), max(0, ys.min() - 8), min(256, xs.max() + 9), min(224, ys.max() + 9))
            nc = Image.open(p).convert('RGB').crop(box)
            key = hashlib.sha1(nc.tobytes()).hexdigest()
            if key in seen:
                continue
            seen.add(key)
            crops.append((name, Image.open(bq).convert('RGB').crop(box), nc))
        print(f'{s}\t{novel} novel\t{len(crops)} regions')
        if crops:
            rows = []
            for name, oc, nc in crops[:24]:
                w, h = oc.size
                r = Image.new('RGB', (w * 2 + 6, h + 10), (255, 0, 255))
                r.paste(oc, (0, 10))
                r.paste(nc, (w + 6, 10))
                ImageDraw.Draw(r).text((1, 0), name, fill=(255, 255, 0))
                rows.append(r)
            W = max(r.width for r in rows)
            H = sum(r.height + 2 for r in rows)
            sheet = Image.new('RGB', (W, H), (40, 40, 40))
            y = 0
            for r in rows:
                sheet.paste(r, (0, y))
                y += r.height + 2
            sheet.resize((W * 2, H * 2), Image.NEAREST).save(os.path.join(a.out, s + '.png'))


if __name__ == '__main__':
    main()
