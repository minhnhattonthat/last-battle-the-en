"""Build, gate and package a release: patch + README in release/LastBattle_EN_vX.Y.zip.

Stops at the first failure: build -> tests -> smoke -> jp_left -> qa_gate check on every work/qa/**/manifest.tsv ->
textcover -> docs/polish.md has no unticked line -> README.md has no template placeholder -> debug tool off ->
SNES checksum -> BPS patch (re-applied by bps.py) -> re-apply to a clean original and compare -> zip.
Never publishes anything. Refuses to overwrite an existing version's files without --force.

    python -X utf8 tools/release.py [--version 1.0] [--force]
"""
import argparse, glob, hashlib, os, re, shutil, subprocess, sys, tempfile, zipfile, zlib

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
ORIG = os.path.join(ROOT, 'rom', 'Last Battle, The (Japan).sfc')
BUILT = os.path.join(ROOT, 'build', 'lastbattle_en.sfc')
PY = [sys.executable, '-X', 'utf8']


def skill():
    from skill import SKILL
    return SKILL


def step(name, cmd, **kw):
    print('==>', name, flush=True)
    r = subprocess.run(cmd, cwd=ROOT, **kw)
    if r.returncode != 0:
        sys.exit('release: %s failed (exit %d)' % (name, r.returncode))


def fail(msg):
    sys.exit('release: ' + msg)


def hashes(data):
    return dict(size=len(data), crc=('%08X' % zlib.crc32(data)), md5=hashlib.md5(data).hexdigest(),
                sha1=hashlib.sha1(data).hexdigest())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--version', default='1.0')
    ap.add_argument('--force', action='store_true', help='overwrite this version\'s existing release files')
    a = ap.parse_args()
    if not re.fullmatch(r'\d+\.\d+(\.\d+)?', a.version):
        fail('version must look like 1.0')
    rel = os.path.join(ROOT, 'release')
    base = 'LastBattle_EN_v%s' % a.version
    bps_out, zip_out = os.path.join(rel, base + '.bps'), os.path.join(rel, base + '.zip')
    if not a.force and (os.path.exists(bps_out) or os.path.exists(zip_out)):
        fail('%s already exists; pass --force to overwrite' % base)
    S = skill()

    # build with no QA/marker/ruler flags: the debug tool is external Lua (tools/debug), never built into the ROM
    step('build', PY + ['build.py'])
    step('tests + lint', PY + ['tools/check.py'])
    step('smoke', PY + [os.path.join(S, 'scripts', 'emu.py'), BUILT, '--out', 'work/qa/release_smoke',
                        '--route', 'tools/routes/boot.txt', '--smoke'])
    step('jp_left', PY + [os.path.join(S, 'scripts', 'jp_left.py'), BUILT, '--tbl', 'tbl/jp.tbl', '--min', '6',
                          '--known', 'docs/jp_known.txt'])
    manifests = sorted(glob.glob(os.path.join(ROOT, 'work', 'qa', '**', 'manifest.tsv'), recursive=True))
    if not manifests:
        fail('no work/qa/**/manifest.tsv found')
    for m in manifests:
        step('qa_gate ' + os.path.relpath(m, ROOT), PY + [os.path.join(S, 'scripts', 'qa_gate.py'), 'check', m,
                                                          os.path.join(os.path.dirname(m), 'verdicts')])
    strings = os.path.join(ROOT, 'work', 'qa', 'cover_build', 'strings.tsv')
    step('textcover', PY + [os.path.join(S, 'scripts', 'textcover.py'), 'work/qa/cover', strings, '--waive',
                            'docs/text_unshown.tsv', '--mask', '0xFFFFFFFFFFFF'], stdout=subprocess.DEVNULL)

    print('==> polish / README / debug checks', flush=True)
    open_lines = [l for l in open(os.path.join(ROOT, 'docs', 'polish.md'), encoding='utf-8') if l.startswith('- [ ]')]
    if open_lines:
        fail('%d unticked line(s) in docs/polish.md' % len(open_lines))
    readme = open(os.path.join(ROOT, 'README.md'), encoding='utf-8').read()
    ph = re.findall(r'<(?:Game title|platform|publisher|year|repo|file|size|sha1|game|ext)>|<[A-Z][a-z]+(?: [a-z/ ]+)>',
                    readme)
    if ph:
        fail('template placeholders left in README.md: %s' % ', '.join(sorted(set(ph))))
    orig = open(ORIG, 'rb').read()
    oh = hashes(orig)
    if oh['sha1'] not in readme:
        fail('README.md does not state the base ROM SHA-1')
    built = open(BUILT, 'rb').read()
    if b'[MARKER' in built or b'warp.lua' in built:
        fail('debug/marker data in the release build')

    os.makedirs(rel, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        fixed = os.path.join(td, 'lastbattle_en.sfc')
        step('snes-checksum', PY + ['tools/bps.py', 'snes-checksum', BUILT, '--out', fixed])
        step('bps make', PY + ['tools/bps.py', 'make', ORIG, fixed, bps_out])
        again = os.path.join(td, 'reapplied.sfc')
        step('bps apply to clean original', PY + ['tools/bps.py', 'apply', ORIG, bps_out, again])
        target = open(fixed, 'rb').read()
        if open(again, 'rb').read() != target:
            fail('re-applied patch differs from the build')
        shutil.copyfile(fixed, os.path.join(ROOT, 'build', 'lastbattle_en_release.sfc'))
    ph_ = hashes(target)
    text = open(os.path.join(ROOT, 'docs', 'release-readme.txt'), encoding='utf-8').read()
    for k, v in dict(VERSION=a.version, SIZE=oh['size'], CRC32=oh['crc'], MD5=oh['md5'], SHA1=oh['sha1'],
                     PSIZE=ph_['size'], PCRC32=ph_['crc'], PSHA1=ph_['sha1'], PATCH=base + '.bps').items():
        text = text.replace('@%s@' % k, str(v))
    if re.search(r'@[A-Z0-9]+@', text):
        fail('unfilled field in docs/release-readme.txt')
    with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.write(bps_out, base + '.bps')
        z.writestr('README.txt', text.replace('\n', '\r\n'))
    print('release: %s (%d bytes): %s + README.txt; patched CRC32 %s SHA-1 %s'
          % (os.path.relpath(zip_out, ROOT), os.path.getsize(zip_out), base + '.bps', ph_['crc'], ph_['sha1']))
    print('release: build/lastbattle_en_release.sfc is the checksum-fixed playable image. Nothing was published.')


if __name__ == '__main__':
    main()
