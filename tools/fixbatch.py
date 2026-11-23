"""Make a fix batch from ids already translated, for review fixes that go through the batch pipeline.

    python -X utf8 tools/fixbatch.py b051 r135_11C9 r138_0710 ...   (or ids from a file: @ids.txt)

Writes work/tl/<name>.tsv (the ids' rows copied from the batches that hold them) and work/tl/<name>.out.tsv seeded
with each id's current English from those batches' .out.tsv. Edit the .out.tsv with the file-edit tool, then
`batches.py check <name>` and `batches.py merge <name> --overwrite`. Refuses to overwrite an existing fix batch.
"""
import glob
import os
import sys

TL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'work', 'tl')


def rows(pattern):
    """id -> row; a later batch (a fix batch) wins over an earlier one."""
    out = {}
    for path in sorted(glob.glob(os.path.join(TL, pattern))):
        with open(path, encoding='utf-8', newline='') as f:
            for line in f.read().split('\n'):
                if line:
                    out[line.split('\t', 1)[0]] = line
    return out


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    name, ids = argv[0], []
    for a in argv[1:]:
        if a.startswith('@'):
            ids += open(a[1:], encoding='utf-8').read().split()
        else:
            ids.append(a)
    tsv, out = os.path.join(TL, name + '.tsv'), os.path.join(TL, name + '.out.tsv')
    if os.path.exists(tsv) or os.path.exists(out):
        sys.exit(f'{name} exists; pick a new batch name')
    src = rows('b[0-9][0-9][0-9].tsv')
    en = rows('b[0-9][0-9][0-9].out.tsv')
    missing = [i for i in ids if i not in src or i not in en]
    if missing:
        sys.exit('not in any batch: ' + ' '.join(missing))
    with open(tsv, 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(src[i] + '\n' for i in ids))
    with open(out, 'w', encoding='utf-8', newline='') as f:
        f.write(''.join(en[i] + '\n' for i in ids))
    print(f'{len(ids)} ids -> {tsv}, {out}')


if __name__ == '__main__':
    main(sys.argv[1:])
