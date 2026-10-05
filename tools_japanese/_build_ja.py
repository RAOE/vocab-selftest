# -*- coding: utf-8 -*-
"""Build _words_ja_final.json from nihonngo-goi (N5N4 + N3)."""
import json, glob, re, sys, collections
sys.stdout.reconfigure(encoding='utf-8')

CIRC = '⓪①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱⑲⑳'
KANA = re.compile(r'[ぁ-ゖァ-ヺー]')
PAREN = re.compile(r'^[（(]([^）)]*)[）)]\s*')
PITCH = re.compile(r'^([%s]+(?:[+＋/・][%s]+)*)\s*' % (CIRC, CIRC))
POS = re.compile(r'^(【[^】]*】)\s*')
STRIP = '）)　 '

def kata2hira(s):
    out = []
    for ch in s:
        o = ord(ch)
        if 0x30A1 <= o <= 0x30F6:
            out.append(chr(o - 0x60))
        else:
            out.append(ch)
    return ''.join(out)

def parse(w, desc, correct):
    desc = (desc or '').strip()
    correct = (correct or '').strip()
    desc = desc.lstrip(STRIP)
    g1 = None
    m = PAREN.match(desc)
    if m:
        g1 = m.group(1).strip()
        desc = desc[m.end():].lstrip(STRIP)
    pitch = ''
    m = PITCH.match(desc)
    if m:
        pitch = m.group(1).split('/')[0].split('・')[0].split('+')[0].split('＋')[0].strip()
        desc = desc[m.end():].lstrip(STRIP)
    pos = ''
    m = POS.match(desc)
    if m:
        pos = m.group(1)
        desc = desc[m.end():].strip()
    meaning = desc.strip(' 　；;，,')
    if not meaning:
        meaning = correct.strip()
    reading = ''
    if g1 and KANA.search(g1):
        reading = g1
    elif KANA.search(w):
        reading = w
    z = (pos + meaning).strip()
    return reading, pitch, z

def main():
    files = sorted(glob.glob('nihonngo-goi-master/n5n4/*.json')) + sorted(glob.glob('nihonngo-goi-master/n3/*.json'))
    lvmap = {'n5n4': 'N5N4', 'n3': 'N3'}
    seen = {}
    bad = []
    n_pitch = 0
    n_meaning_fallback = 0
    for path in files:
        lv = lvmap[path.replace('\\', '/').split('/')[1]]
        d = json.load(open(path, encoding='utf-8'))
        for e in d['data']:
            w = (e.get('wordName') or '').strip()
            raw_desc = (e.get('wordDesc') or '').strip()
            reading, pitch, z = parse(w, raw_desc, e.get('correctDesc'))
            if not w or not z:
                bad.append((path, w, raw_desc)); continue
            if pitch: n_pitch += 1
            else: n_meaning_fallback += 1  # purely a no-pitch counter
            # sanity: if desc had a pitch-looking token but we missed it
            if re.match(r'^[%s]' % CIRC, raw_desc.lstrip(STRIP).replace('）', '').replace(')', '')) and not pitch:
                bad.append((path, w, raw_desc)); continue
            key = (w, reading)
            if key in seen:
                continue
            seen[key] = {'w': w, 'i': reading if reading != w else '', 'p': pitch, 'z': z, 'lv': lv}
    words = list(seen.values())
    lvord = {'N5N4': 0, 'N3': 1}
    words.sort(key=lambda x: (lvord[x['lv']], kata2hira(x['i'] or x['w'])))
    with open('_words_ja_final.json', 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, separators=(',', ':'))
    fin_pitch = sum(1 for x in words if x['p'])
    print('total parsed:', len(words), '| with pitch:', fin_pitch, '| no pitch:', len(words) - fin_pitch)
    print('lv dist:', collections.Counter(x['lv'] for x in words))
    print('bad/unparsed:', len(bad))
    for b in bad[:30]: print('BAD:', b[0], '|', repr(b[1]), '|', repr(b[2]))
    # duplicate word check (same word different reading)
    wd = collections.Counter(x['w'] for x in words)
    dupw = [(w, c) for w, c in wd.items() if c > 1]
    print('same-word multi-reading:', len(dupw), dupw[:10])
    # no-reading check
    noread = [x for x in words if not x['i']]
    print('entries where reading==word (i empty):', len(noread))
    print('samples:')
    for x in words[:3] + words[1990:1993] + words[-3:]:
        print(' ', x['w'], '|', x['i'], '|', x['p'], '|', x['z'], '|', x['lv'])

main()
