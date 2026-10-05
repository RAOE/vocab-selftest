# -*- coding: utf-8 -*-
"""开发版：三套词表批量发音音频（edge-tts 免费合成，可断点续跑）。
用法：python gen_audio.py [每套前N个]   留空=全量"""
import asyncio
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

import edge_tts

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
CONCURRENCY = 8
RETRY = 4

JOBS = [
    ('b', os.path.join(ROOT, 'tools_basic3000', '_words_final.json'), 'en-GB-SoniaNeural'),
    ('e', os.path.join(ROOT, 'tools_basic3000', '_words_ielts_final.json'), 'en-GB-SoniaNeural'),
    ('j', os.path.join(ROOT, 'tools_japanese', '_words_ja_final.json'), 'ja-JP-NanamiNeural'),
]


def build_tasks(limit):
    tasks = []
    for app, path, voice in JOBS:
        words = json.load(open(path, encoding='utf-8'))
        outdir = os.path.join(BASE, 'audio', app)
        os.makedirs(outdir, exist_ok=True)
        n = len(words) if not limit else min(limit, len(words))
        for idx in range(n):
            e = words[idx]
            if app == 'j':
                text = (e.get('i') or e.get('w') or '').strip()
            else:
                text = (e.get('w') or '').strip()
            if text:
                tasks.append((os.path.join(outdir, '%d.mp3' % idx), text, voice))
        print('app %s: %d words (target %d)' % (app, len(words), n), flush=True)
    return tasks


async def gen_one(out, text, voice, sem, st):
    async with sem:
        if os.path.exists(out) and os.path.getsize(out) > 300:
            st['skip'] += 1
        else:
            err = ''
            for att in range(RETRY):
                try:
                    c = edge_tts.Communicate(text, voice)
                    await c.save(out)
                    if os.path.exists(out) and os.path.getsize(out) > 300:
                        st['ok'] += 1
                        err = ''
                        break
                    raise RuntimeError('empty file')
                except Exception as e:
                    err = str(e)[:120]
                    await asyncio.sleep(1.0 + 2.0 * att)
            else:
                st['fail'] += 1
                st['failed'].append('%s\t%s\t%s' % (out, text, err))
        done = st['ok'] + st['skip'] + st['fail']
        if done % 200 == 0:
            el = time.time() - st['t0']
            rate = done / el if el > 0 else 0
            print('[%5.0fs] ok=%d skip=%d fail=%d / %d  (%.1f/s)' % (
                el, st['ok'], st['skip'], st['fail'], st['total'], rate), flush=True)


async def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    tasks = build_tasks(limit)
    st = {'ok': 0, 'skip': 0, 'fail': 0, 'failed': [], 't0': time.time(), 'total': len(tasks)}
    print('total tasks:', len(tasks), flush=True)
    sem = asyncio.Semaphore(CONCURRENCY)
    await asyncio.gather(*(gen_one(o, t, v, sem, st) for o, t, v in tasks))
    el = time.time() - st['t0']
    print('DONE in %.0fs  ok=%d skip=%d fail=%d' % (el, st['ok'], st['skip'], st['fail']), flush=True)
    if st['failed']:
        with open(os.path.join(BASE, 'gen_failed.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(st['failed']))
        print('failed list -> gen_failed.txt (%d)' % len(st['failed']), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
