# -*- coding: utf-8 -*-
"""Build IELTS word list: ECDICT rows tagged 'ielts' minus basic-list overlap.

Diagnostics first: inspect plural drops, translation cleaning, IPA coverage.
"""
import csv
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'
csv.field_size_limit(10 ** 9)

basic = json.load(io.open(BASE + r'\_words_final.json', encoding='utf-8'))
basic_set = set(e['w'].lower() for e in basic)

ielts_rows = []
with io.open(BASE + r'\ecdict.csv', encoding='utf-8-sig', newline='') as f:
    r = csv.DictReader(f)
    for row in r:
        tag = (row.get('tag') or '')
        if 'ielts' in tag.split():
            ielts_rows.append(row)
ielts_set = set(r['word'].strip().lower() for r in ielts_rows)
union = basic_set | ielts_set
print('ielts rows:', len(ielts_rows), '| basic:', len(basic_set), '| overlap:', len(basic_set & ielts_set))


def not_basic(r):
    return r['word'].strip().lower() not in basic_set


cand = [r for r in ielts_rows if not_basic(r)]
print('candidates (ielts - basic):', len(cand))

# ---- 1) drop plurals whose lemma is in the union ----
def lemma_cands(w):
    c = set()
    if w.endswith('ies') and len(w) > 4:
        c.add(w[:-3] + 'y')
    if w.endswith('es'):
        c.add(w[:-2])
        c.add(w[:-1])
    if w.endswith('s') and not w.endswith('ss'):
        c.add(w[:-1])
    if w.endswith('ves'):
        c.add(w[:-3] + 'f')
        c.add(w[:-3] + 'fe')
    return c


plural_drop = []
for r in cand[:]:
    w = r['word'].strip().lower()
    if ' ' in w or '-' in w:
        continue
    if w.endswith('s') and not w.endswith('ss') and len(w) > 3:
        for c in lemma_cands(w):
            if c in union:
                plural_drop.append(r['word'])
                cand.remove(r)
                break
print('plural dropped:', len(plural_drop))
print(' ', ', '.join(plural_drop))

# US->UK spelling merge: drop US variant if UK variant present in union
def brit_cands(x):
    c = set()
    if x.endswith('or'):
        c.add(x[:-2] + 'our')
    if x.endswith('er'):
        c.add(x[:-2] + 're')
    if x.endswith('og'):
        c.add(x + 'ue')
    if x.endswith('ize'):
        c.add(x[:-3] + 'ise')
    if x.endswith('yze'):
        c.add(x[:-3] + 'yse')
    if x.endswith('gram'):
        c.add(x + 'me')
    if x.endswith('ense'):
        c.add(x[:-3] + 'ence')
    return c


spell_drop = []
for r in cand[:]:
    w = r['word'].strip().lower()
    for c in brit_cands(w):
        if c in union:
            spell_drop.append((r['word'], c))
            cand.remove(r)
            break
print('spelling-variant dropped:', len(spell_drop), spell_drop)

# ---- 2) clean translation ----
def clean_zh(raw):
    lines = [l.strip() for l in (raw or '').replace('\r', '').split('\n')]
    out = []
    for l in lines:
        if not l:
            continue
        if re.match(r'^\[网络\]', l):
            continue
        l = re.sub(r'^\[[^\]]{1,6}\]\s*', '', l)
        l = re.sub(r'\s+', ' ', l).strip()
        if not l:
            continue
        if re.search(r'人名|姓氏|俚', l):
            l2 = '; '.join(p.strip() for p in re.split(r'[;；]', l)
                           if p.strip() and not re.search(r'人名|姓氏|俚', p))
            l = l2
        if l:
            out.append(l)
    s = '; '.join(out)
    return s


def truncate_zh(s, cap=58):
    if len(s) <= cap:
        return s
    cut = s[:cap]
    for sep in ('; ', '；', '，', ',', ' '):
        i = cut.rfind(sep)
        if i >= cap * 0.5:
            return cut[:i].rstrip(' ;；,，') + '…'
    return cut + '…'


empty_zh = []
for r in cand[:]:
    z = truncate_zh(clean_zh(r['translation']))
    if not z:
        empty_zh.append(r['word'])
        cand.remove(r)
    r['_zh'] = z
print('dropped for empty zh:', len(empty_zh), empty_zh)

print('\n== zh samples ==')
for r in cand[:8] + cand[500:505]:
    print('  %-16s | %s' % (r['word'], r['_zh']))

# ---- 3) sanity: weird entries ----
weird = [r['word'] for r in cand if re.search(r'\d|\.', r['word']) or len(r['word']) <= 2]
print('\nweird entries:', weird)

# ---- 4) IPA coverage ----
def load_ipa(path):
    d = {}
    for line in io.open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line or '\t' not in line:
            continue
        w, pr = line.split('\t', 1)
        w = w.strip().lower()
        if w in d:
            continue
        pr = pr.strip().split(',')[0].strip()
        if pr.startswith('/') and pr.endswith('/'):
            pr = pr[1:-1]
        d[w] = pr
    return d


uk = load_ipa(BASE + r'\ipa_en_UK.txt')
us = load_ipa(BASE + r'\ipa_en_US.txt')
miss = [r['word'] for r in cand if r['word'].lower() not in uk and r['word'].lower() not in us]
print('\nIPA missing (%d):' % len(miss))
print(miss)

n_uk = sum(1 for r in cand if r['word'].lower() in uk)
n_us = sum(1 for r in cand if r['word'].lower() not in uk and r['word'].lower() in us)
print('IPA source: uk=%d us=%d missing=%d total=%d' % (n_uk, n_us, len(miss), len(cand)))

json.dump([{'w': r['word'], 'zh': r['_zh'], 'frq': r['frq'], 'bnc': r['bnc']} for r in cand],
          io.open(BASE + r'\_ielts_cand.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('\ndumped _ielts_cand.json:', len(cand))
