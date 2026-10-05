# -*- coding: utf-8 -*-
"""Prepare final word list: drop junk, clean zh clauses, attach IPA (UK->US->manual)."""
import json, io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'

u = json.load(io.open(BASE + r'\_union.json', encoding='utf-8'))

# junk entries to drop (typos / abbreviation noise / wrong-sense entries)
DROP = {'rusia', 'behavious', 'hur', 'gy', 'dr', 'vcd', 'mm', 'pm', 'ad', 'chain stores'}
# display-case fixes
CASE_FIX = {'x-ray': 'X-ray'}

# manual IPA overrides/fills (take precedence over the dictionaries)
MANUAL_IPA = {
    'beancurd': 'ˈbiːnkɜːd', 'beddings': 'ˈbedɪŋz', 'handtruck': 'ˈhandtrʌk',
    'sideway': 'ˈsaɪdweɪ', 'maths': 'mæθs', 'offence': 'əˈfens',
    'passer-by': 'ˌpɑːsəˈbaɪ', 'used to': 'ˈjuːst tu', 'chain store': 'ˈtʃeɪn stɔː',
    'hard-working': 'ˌhɑːdˈwɜːkɪŋ', 'non-stop': 'ˌnɒnˈstɒp', 'x-ray': 'ˈeksreɪ',
    'e-mail': 'ˈiːmeɪl',
}


def clean_zh2(s):
    parts = [p.strip() for p in re.split(r'[;；]', s)]
    out = []
    for p in parts:
        if not p:
            continue
        if '人名' in p or '姓氏' in p or '俚' in p:
            continue
        out.append(p)
    s = '; '.join(out)
    s = re.sub(r'([，、。！？：])\s+', r'\1', s)
    return s


entries = []
for e in u:
    k = e['word'].lower()
    if k in DROP:
        continue
    w = CASE_FIX.get(k, e['word'])
    zh = e['zh']
    if k == 'am':
        zh = 'v. 是（be 动词第一人称单数现在式）'
    zh = clean_zh2(zh)
    entries.append({'w': w, 'z': zh})

# ---- IPA ----
VOW = set('aeiouɑɒɔəɜʌʊɪæɛɐᵻɚɝø')
CONS = set('pbtdkɡgfvθðszʃʒçhɦmnŋlrɹjwʍ')
ON2 = {'pl', 'pr', 'bl', 'br', 'tr', 'dr', 'kl', 'kr', 'gl', 'gr', 'fl', 'fr',
       'θr', 'ʃr', 'sl', 'sw', 'sp', 'st', 'sk', 'sm', 'sn', 'tw', 'dw', 'gw',
       'kw', 'hw', 'pj', 'bj', 'kj', 'gj', 'fj', 'vj', 'mj', 'nj', 'lj', 'sj',
       'zj', 'hj', 'tʃ', 'dʒ'}
ON3 = {'spr', 'str', 'skr', 'spl', 'skw', 'spj', 'stj', 'skj', 'skl'}
CHARMAP = {'ɐ': 'ə', 'ɛ': 'e', 'ɡ': 'g', 'ɹ': 'r', 'ᵻ': 'ɪ', 'ɫ': 'l', 'ɝ': 'ɜː', 'ɚ': 'ə'}


def valid_onset(c):
    if len(c) == 1:
        return c in CONS
    if len(c) == 2:
        return c in ON2
    if len(c) == 3:
        return c in ON3
    return False


def move_marks(s):
    for mark in ('ˈ', 'ˌ'):
        i = s.find(mark)
        if i <= 0:
            continue
        j = i
        while j - 1 >= 0 and s[j - 1] in CONS:
            j -= 1
        run = s[j:i]
        if not run:
            continue
        best = None
        for L in range(min(3, len(run)), 0, -1):
            cand = run[-L:]
            if valid_onset(cand):
                best = L
                break
        if best is None:
            best = 1
        newpos = j + (len(run) - best)
        s = s[:i] + s[i + 1:]
        s = s[:newpos] + mark + s[newpos:]
    return s


def syll_count(s):
    t = s.replace('ˈ', '').replace('ˌ', '').replace('ː', '')
    dip = {'aɪ', 'aʊ', 'eɪ', 'ɔɪ', 'əʊ', 'ɪə', 'eə', 'ʊə', 'iə', 'uə', 'oʊ'}
    n = 0
    i = 0
    while i < len(t):
        if t[i] in VOW:
            n += 1
            if i + 1 < len(t) and t[i:i + 2] in dip:
                i += 2
                continue
        i += 1
    return n


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

miss = []
for e in entries:
    k = e['w'].lower()
    ipa = MANUAL_IPA.get(k) or uk.get(k) or us.get(k) or ''
    src = 'manual' if k in MANUAL_IPA else ('uk' if k in uk else ('us' if k in us else 'none'))
    e['src'] = src
    if ipa:
        ipa = ''.join(CHARMAP.get(c, c) for c in ipa)
        ipa = move_marks(ipa)
        if syll_count(ipa) <= 1:
            ipa = ipa.replace('ˈ', '').replace('ˌ', '')
    else:
        miss.append(e['w'])
    e['i'] = ipa

entries.sort(key=lambda e: e['w'].lower())
json.dump(entries, io.open(BASE + r'\_words_final.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)

n_uk = sum(1 for e in entries if e['src'] == 'uk')
n_us = sum(1 for e in entries if e['src'] == 'us')
print('total:', len(entries), '| uk:', n_uk, '| us:', n_us, '| manual:', sum(1 for e in entries if e['src'] == 'manual'))
print('missing ipa (%d):' % len(miss))
print(miss)

print('\n== QA samples ==')
known = {e['w'].lower(): e for e in entries}
for w in ['medicine', 'floor', 'colour', 'climb', 'challenge', 'harvest', 'accept',
          'theatre', 'x-ray', 'hundred', 'absorb', 'computer', 'beautiful', 'superman',
          'kangaroo', 'wednesday', 'water', 'English', 'study']:
    e = known.get(w.lower())
    if e:
        print('%-12s /%s/  | %s' % (e['w'], e['i'], e['z'][:46]))
    else:
        print('%-12s MISSING' % w)

print('\n== first 20 alphabetically ==')
for e in entries[:20]:
    print('%-14s /%s/ | %s' % (e['w'], e['i'], e['z'][:46]))

import random
random.seed(7)
print('\n== 20 random ==')
for e in random.sample(entries, 20):
    print('%-16s /%s/ | %s' % (e['w'], e['i'], e['z'][:50]))

# leftover junk scan
print('\n== leftover scan ==')
bad = 0
for e in entries:
    if re.search(r'人名|姓氏|俚', e['z']):
        bad += 1
        print(' zh junk:', e['w'], e['z'][:40])
    if e['i'] and re.search(r'[^\x00-\x7fɑɒɔəɜʌʊɪæɛɐɚɝøθðʃʒŋɡɹʍçɦːˈˌ\u0250-\u02ff]', e['i']):
        print(' ipa odd chars:', e['w'], repr(e['i']))
print('done. bad zh:', bad)
