# -*- coding: utf-8 -*-
"""Merge junior+senior word lists, dedupe spelling variants, join ECDICT (ipa/freq)."""
import json, io, sys, csv, re
from collections import OrderedDict
sys.stdout.reconfigure(encoding='utf-8')
BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'


def fmt_ts(ts):
    parts = []
    for t in (ts or []):
        tr = re.sub(r'\s+', ' ', (t.get('translation') or '').strip())
        ty = (t.get('type') or '').strip()
        parts.append((ty + '. ' if ty else '') + tr)
    return '; '.join(parts)


def clean_zh(s):
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'；\s+', '；', s)
    return s.strip(' ;')


j = json.load(io.open(BASE + r'\junior.json', encoding='utf-8'))
s = json.load(io.open(BASE + r'\senior.json', encoding='utf-8'))

jw = set(x['word'].strip().lower() for x in j)
sw = set(x['word'].strip().lower() for x in s)

entries = OrderedDict()
for x in j:
    w = x['word'].strip()
    entries[w.lower()] = {'word': w, 'zh': clean_zh(fmt_ts(x.get('translations'))), 'src': 'j'}
for x in s:
    w = x['word'].strip()
    k = w.lower()
    zh = clean_zh(fmt_ts(x.get('translations')))
    if k in entries:
        entries[k]['word'] = w
        entries[k]['src'] = 'j+s'
        if zh:
            entries[k]['zh'] = zh
    else:
        entries[k] = {'word': w, 'zh': zh, 'src': 's'}

print('union total:', len(entries))

drop = []
for k in list(entries):
    w = entries[k]['word']
    if len(w) <= 1 or ('.' in w) or re.search(r'\d', w):
        drop.append(k)
print('noise dropped:', len(drop), [entries[k]['word'] for k in drop][:50])
for k in drop:
    del entries[k]

# American spelling (junior-only) -> British variant (senior) merge
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
    return c


merged = []
for k in sorted(entries):
    if k in jw and k not in sw:
        for c in brit_cands(k):
            if c in entries:
                merged.append((k, c))
                del entries[k]
                break
print('variant merges:', len(merged), merged[:40])

print('after cleaning:', len(entries))

# join ECDICT
need = set(entries.keys())
ec = {}
with io.open(BASE + r'\ecdict.csv', encoding='utf-8-sig', newline='') as f:
    r = csv.reader(f)
    header = next(r)
    print('ecdict header:', header)
    idx = {name: i for i, name in enumerate(header)}
    FIELDS = ('phonetic', 'translation', 'bnc', 'frq', 'tag', 'collins', 'oxford')
    for row in r:
        if len(row) < len(header):
            continue
        w = row[idx['word']].strip().lower()
        if w in need:
            cur = ec.setdefault(w, {f: '' for f in FIELDS})
            for fld in FIELDS:
                v = row[idx[fld]].strip()
                if v and not cur[fld]:
                    cur[fld] = v

missing = [k for k in entries if k not in ec]
noipa = [k for k in entries if k in ec and not ec[k]['phonetic']]
nofrq = [k for k in entries if k in ec and not ec[k]['frq'] and not ec[k]['bnc']]
nozh = [k for k in entries if not entries[k]['zh']]
print('missing in ecdict:', len(missing), missing[:30])
print('no phonetic:', len(noipa), noipa[:30])
print('no frq/bnc rank:', len(nofrq), nofrq[:40] if len(nofrq) < 60 else '')
print('no zh:', len(nozh), nozh[:20])

print('\nsample phonetics:')
for w in ['floor', 'medicine', 'colour', 'climb', 'harvest', 'challenge', 'accept']:
    print(' ', w, '->', ec.get(w, {}).get('phonetic'), '| frq:', ec.get(w, {}).get('frq'), '| bnc:', ec.get(w, {}).get('bnc'))

def rank_of(k):
    e = ec.get(k)
    if not e:
        return 10**9
    fr = e['frq'] or e['bnc']
    if not fr:
        return 10**9
    try:
        return int(fr)
    except Exception:
        return 10**9


ordered = sorted(entries, key=rank_of)
for n in (2500, 2800, 3000, 3200, 3400, 3600, 3800):
    if n < len(ordered):
        w = ordered[n - 1]
        print('rank#%d boundary word: %s (frq=%s bnc=%s)' % (n, w, ec.get(w, {}).get('frq'), ec.get(w, {}).get('bnc')))

print('\nwords 2980-3030 by frequency:')
print(', '.join(ordered[2979:3030]))
print('\nwords 3180-3230 by frequency:')
print(', '.join(ordered[3179:3230]))
print('\nwords 3380-3430 by frequency:')
print(', '.join(ordered[3379:3430]))
print('\nwords 3680-3740 by frequency:')
print(', '.join(ordered[3679:3740]))

nofreq = [k for k in entries if rank_of(k) == 10**9]
print('\nno freq rank words (%d):' % len(nofreq), ', '.join(sorted(nofreq)))

# short words review (len<=3 after removing apostrophes)
short = [k for k in entries if len(k.replace("'", '')) <= 3]
print('\nshort words (%d):' % len(short))
for k in sorted(short):
    print(' ', entries[k]['word'], '|', entries[k]['zh'][:40], '| src:', entries[k]['src'])

# no-ipa words with zh
print('\nno-ipa words with zh:')
for k in noipa:
    print(' ', entries[k]['word'], '|', entries[k]['zh'][:40], '| src:', entries[k]['src'])

# dump cleaned union with ec info
out = []
for k in ordered:
    e = entries[k]
    d = ec.get(k, {})
    out.append({
        'word': e['word'], 'zh': e['zh'], 'src': e['src'],
        'ec_ipa': d.get('phonetic', ''), 'frq': d.get('frq', ''), 'bnc': d.get('bnc', ''),
        'tag': d.get('tag', ''), 'collins': d.get('collins', ''), 'oxford': d.get('oxford', ''),
    })
json.dump(out, io.open(BASE + r'\_union.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print('\ndumped _union.json with', len(out), 'entries')
