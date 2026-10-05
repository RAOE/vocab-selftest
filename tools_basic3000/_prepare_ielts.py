# -*- coding: utf-8 -*-
"""Build final IELTS word list (advanced = beyond the 3887 basic list).

Source: ECDICT rows tagged 'ielts' (5040) minus basic overlap (1808)
        minus plural/name-junk entries -> cleaned zh + IPA (UK->US->manual).
Output: _words_ielts_final.json  (same schema as _words_final.json: w/i/z)
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
    for row in csv.DictReader(f):
        if 'ielts' in (row.get('tag') or '').split():
            ielts_rows.append(row)
ielts_set = set(r['word'].strip().lower() for r in ielts_rows)
union = basic_set | ielts_set
print('ielts:', len(ielts_rows), '| basic:', len(basic_set), '| overlap:', len(basic_set & ielts_set))

cand = [r for r in ielts_rows if r['word'].strip().lower() not in basic_set]

# ---- plural forms whose lemma already exists ----
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

# ---- US spelling duplicate of an existing UK word ----
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

# ---- clean translation ----
NAME_JUNK = re.compile(r'（人名）|（姓氏）|（男子名）|（女子名）|（昵称）|\[人名\]|^人名$|^姓氏$')
PAREN_JUNK = re.compile(r'\(俚\)|（俚）|\[俚\]')


def dedupe_parts(s):
    parts = [p.strip() for p in s.split('; ') if p.strip()]
    out = []
    seen = set()
    prev_pos = None
    for p in parts:
        m = re.match(r'^([a-z]{1,5}\.)\s*', p)
        pos = m.group(1) if m else None
        body = re.sub(r'^[a-z]{1,5}\.\s*', '', p)
        toks = [t.strip() for t in re.split(r'[,，、]', body) if t.strip()]
        unseen = [t for t in toks if t not in seen]
        same_pos = (pos is None) or (pos == prev_pos)
        if same_pos and toks and (not unseen or (len(unseen) <= 1 and len(toks) >= 3)):
            continue
        seen.update(toks)
        if pos:
            prev_pos = pos
        out.append(p)
    return '; '.join(out)


def clean_zh(raw):
    raw = (raw or '').replace('\\n', '\n')
    lines = [l.strip() for l in raw.replace('\r', '').split('\n')]
    out = []
    for l in lines:
        if not l or re.match(r'^\[网络\]', l):
            continue
        l = re.sub(r'^\[[^\]]{1,6}\]\s*', '', l)
        l = re.sub(r'\s+', ' ', l).strip()
        if not l:
            continue
        parts = [p.strip() for p in re.split(r'[;；]', l)]
        parts = [p for p in parts if p and not NAME_JUNK.search(p) and not PAREN_JUNK.search(p)]
        l = '; '.join(parts).strip()
        if l:
            out.append(l)
        if len(out) >= 3:
            break
    return dedupe_parts('; '.join(out))


def truncate_zh(s, cap=58):
    if len(s) <= cap:
        return s
    cut = s[:cap]
    for sep in ('; ', '；', '，', ',', ' '):
        i = cut.rfind(sep)
        if i >= cap * 0.5:
            return cut[:i].rstrip(' ;；,，') + '…'
    return cut + '…'


ZH_OVERRIDE = {
    'drop-out': 'n. 中途退学者, 辍学者; 退出, 离开（社会主流等）',
}

clean_rows = []
name_drop = []
for r in cand:
    w = r['word'].strip()
    z = truncate_zh(clean_zh(r['translation']))
    if not z:
        name_drop.append(w)
        continue
    if w[0].isupper() and re.search(r'人名|姓氏', r['translation'] or ''):
        name_drop.append(w)
        continue
    if w.lower() in ZH_OVERRIDE:
        z = ZH_OVERRIDE[w.lower()]
    r['_zh'] = z
    clean_rows.append(r)
print('plural dropped:', len(plural_drop), '| spelling dropped:', len(spell_drop),
      '| name/no-zh dropped:', len(name_drop), name_drop)

cand = clean_rows

# ---- IPA ----
MANUAL_IPA = {
    'account for': 'əˈkaʊnt fɔː', 'booklist': 'ˈbʊklɪst', 'bring about': 'ˌbrɪŋ əˈbaʊt',
    'carcase': 'ˈkɑːkəs', 'cd-rom': 'ˌsiːdiːˈrɒm', 'co-operation': 'kəʊˌɒpəˈreɪʃn',
    'coeducation': 'ˌkəʊedjuˈkeɪʃn', 'defile': 'dɪˈfaɪl', 'drop-out': 'ˈdrɒpaʊt',
    'first-aid': 'ˌfɜːstˈeɪd', 'flourishment': 'ˈflɜːrɪʃmənt', 'fund-raising': 'ˈfʌndreɪzɪŋ',
    'gaol': 'dʒeɪl', 'high-rise': 'ˈhaɪraɪz', 'low-risk': 'ˌləʊˈrɪsk',
    'maltreat': 'ˌmælˈtriːt', 'mischance': 'ˌmɪsˈtʃɑːns', 'non-drinker': 'ˌnɒnˈdrɪŋkə',
    'open-book': 'ˌəʊpənˈbʊk', 'phone-in': 'ˈfəʊnɪn', 'preposition': 'ˌprepəˈzɪʃn',
    'reflectance': 'rɪˈflektəns', 'second-hand': 'ˌsekəndˈhænd',
    'self-discipline': 'ˌselfˈdɪsəplɪn', 'superintend': 'ˌsuːpərɪnˈtend',
    'up-to-date': 'ˌʌptəˈdeɪt', 'waggon': 'ˈwæɡən', 'water-clock': 'ˈwɔːtəklɒk',
    'water-proof': 'ˈwɔːtəpruːf', 'water-skiing': 'ˈwɔːtəskiːɪŋ',
    'wollongong': 'ˈwʊləŋɡɒŋ', 'wreathe': 'riːð',
}
DROP_JUNK = {'ohp'}

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

CASE_FIX = {'phd': 'PhD'}

entries = []
miss = []
for r in cand:
    k = r['word'].strip().lower()
    if k in DROP_JUNK:
        continue
    word = CASE_FIX.get(k, r['word'].strip())
    ipa = MANUAL_IPA.get(k) or uk.get(k) or us.get(k) or ''
    src = 'manual' if k in MANUAL_IPA else ('uk' if k in uk else ('us' if k in us else 'none'))
    if not ipa:
        miss.append(word)
    else:
        ipa = ''.join(CHARMAP.get(c, c) for c in ipa)
        if src != 'manual':  # manual entries are already in display form
            ipa = move_marks(ipa)
        if syll_count(ipa) <= 1:
            ipa = ipa.replace('ˈ', '').replace('ˌ', '')
    entries.append({'w': word, 'i': ipa, 'z': r['_zh'], 'src': src})

entries.sort(key=lambda e: e['w'].lower())
json.dump(entries, io.open(BASE + r'\_words_ielts_final.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=0)

print('FINAL:', len(entries))
print('ipa source: uk=%d us=%d manual=%d none=%d' % (
    sum(1 for e in entries if e['src'] == 'uk'),
    sum(1 for e in entries if e['src'] == 'us'),
    sum(1 for e in entries if e['src'] == 'manual'),
    sum(1 for e in entries if e['src'] == 'none')))
print('missing ipa (%d):' % len(miss), miss)

print('\n== first 15 ==')
for e in entries[:15]:
    print('  %-16s /%s/ | %s' % (e['w'], e['i'], e['z'][:44]))
print('== last 10 ==')
for e in entries[-10:]:
    print('  %-16s /%s/ | %s' % (e['w'], e['i'], e['z'][:44]))

import random
random.seed(11)
print('== 25 random ==')
for e in random.sample(entries, 25):
    print('  %-16s /%s/ | %s' % (e['w'], e['i'], e['z'][:50]))

# sanity scans
print('\nsanity:')
bad = 0
for e in entries:
    if not e['i'] or not e['z']:
        bad += 1
        print('  EMPTY:', e)
    if re.search(r'人名|姓氏|\[网络\]|\\n', e['z']):
        bad += 1
        print('  JUNK ZH:', e['w'], e['z'][:40])
print('bad:', bad)

short = [e['w'] for e in entries if len(e['w']) <= 3]
print('short words (%d):' % len(short), short)
