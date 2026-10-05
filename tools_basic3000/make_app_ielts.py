# -*- coding: utf-8 -*-
"""Generate the IELTS self-test app from make_app.py with text substitutions.

Keeps make_app.py as the single source of truth for the 极速刷词 UI;
only data source, titles, storage key and file names differ.
"""
import io
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'

src = io.open(os.path.join(BASE, 'make_app.py'), encoding='utf-8').read()
REPLACEMENTS = [
    ('_words_final.json', '_words_ielts_final.json'),
    ("'vocab_selftest_v1'", "'vocab_selftest_ielts_v1'"),
    ('英语基础词表', '英语雅思词表'),
    ('英语自测结果', '英语雅思自测结果'),
    ('_app.html', '_app_ielts.html'),
]
for a, b in REPLACEMENTS:
    assert a in src, 'missing pattern: ' + a
    src = src.replace(a, b)

g = {'__file__': os.path.join(BASE, 'make_app.py'), '__name__': '__main__'}
exec(compile(src, 'make_app.py(ielts)', 'exec'), g)
