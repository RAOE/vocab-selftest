# -*- coding: utf-8 -*-
"""把 audio_dev/audio/ 的 48kbps 音频批量转码为 32kbps，直接写入两个待部署站点文件夹：
  audio/b -> audio_sites/en/audio/b
  audio/e -> audio_sites/en/audio/e
  audio/j -> audio_sites/ja/audio/j
可重复运行（输出已存在且大于 1KB 时跳过）。完成后打印每目录的数量与体积校验。"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import imageio_ffmpeg

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'audio')
OUT = os.path.join(ROOT, 'audio_sites')
LOG = os.path.join(OUT, 'transcode.log')

MAP = [
    ('b', 'en/audio/b', 3887),
    ('e', 'en/audio/e', 2946),
    ('j', 'ja/audio/j', 3961),
]

FF = imageio_ffmpeg.get_ffmpeg_exe()
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
WORKERS = min(8, max(4, os.cpu_count() or 4))


def convert(pair):
    src, dst = pair
    if os.path.exists(dst) and os.path.getsize(dst) > 1024:
        return 'skip'
    tmp = dst + '.tmp'
    r = subprocess.run(
        [FF, '-v', 'error', '-nostdin', '-y', '-i', src,
         '-b:a', '32k', '-ac', '1', '-ar', '24000', '-f', 'mp3', tmp],
        capture_output=True, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        if os.path.exists(tmp):
            os.remove(tmp)
        return 'fail:' + src
    os.replace(tmp, dst)
    return 'ok'


def main():
    jobs = []
    for sub, rel, expect in MAP:
        sdir = os.path.join(SRC, sub)
        ddir = os.path.join(OUT, rel)
        os.makedirs(ddir, exist_ok=True)
        names = [n for n in os.listdir(sdir) if n.endswith('.mp3')]
        if len(names) != expect:
            raise SystemExit('source count mismatch %s: %d != %d' % (sub, len(names), expect))
        for name in sorted(names, key=lambda n: int(n.split('.')[0])):
            jobs.append((os.path.join(sdir, name), os.path.join(ddir, name)))

    total = len(jobs)
    print('total files: %d, workers: %d, ffmpeg: %s' % (total, WORKERS, FF), flush=True)
    t0 = time.time()
    ok = skip = 0
    fails = []
    logf = open(LOG, 'w', encoding='utf-8')
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for n, res in enumerate(ex.map(convert, jobs), 1):
            if res == 'ok':
                ok += 1
            elif res == 'skip':
                skip += 1
            else:
                fails.append(res)
                logf.write(res + '\n')
                logf.flush()
            if n % 300 == 0 or n == total:
                print('progress %d/%d  ok=%d skip=%d fail=%d  %.0fs' % (
                    n, total, ok, skip, len(fails), time.time() - t0), flush=True)
    logf.close()
    print('DONE ok=%d skip=%d fail=%d  %.0fs' % (ok, skip, len(fails), time.time() - t0), flush=True)
    for f in fails[:20]:
        print('FAIL:', f)

    print('--- verify ---', flush=True)
    all_good = True
    for sub, rel, expect in MAP:
        ddir = os.path.join(OUT, rel)
        names = sorted(n for n in os.listdir(ddir) if n.endswith('.mp3'))
        sizes = [os.path.getsize(os.path.join(ddir, n)) for n in names]
        mib = sum(sizes) / 1048576
        status = 'OK' if len(names) == expect else 'COUNT MISMATCH'
        if len(names) != expect:
            all_good = False
        print('%-14s %d files (expect %d) %.1f MiB  min=%dB avg=%dB max=%dB  -> %s' % (
            rel, len(names), expect, mib, min(sizes), sum(sizes) // len(sizes), max(sizes), status), flush=True)
    tmps = []
    for dirpath, _, filenames in os.walk(OUT):
        tmps += [os.path.join(dirpath, f) for f in filenames if f.endswith('.tmp')]
    print('leftover tmp files:', len(tmps), ' all counts ok:', all_good, flush=True)


main()
