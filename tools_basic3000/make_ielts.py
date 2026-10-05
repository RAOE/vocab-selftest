# -*- coding: utf-8 -*-
"""Build printable IELTS-vocabulary checklist PDF from _words_ielts_final.json.

Same layout as the basic list: A4, compact two-column, checkbox + √/× line.
"""
import html
import io
import json
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

BASE = r'D:\xuyuanfeng_qoder\tools_basic3000'
DESK = r'C:\Users\Administrator\Desktop'
OUT_PDF_NAME = '英语雅思词表-自测勾叉版.pdf'

BROWSERS = [
    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
    r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
]

CSS = '''
@page { size: A4; margin: 6.5mm 6mm 7mm; }
* { box-sizing: border-box; }
body { font-family: "Segoe UI","Microsoft YaHei",Arial,sans-serif; color:#141414;
       font-size:8.3pt; margin:0; line-height:1.22;
       -webkit-print-color-adjust:exact; print-color-adjust:exact; }
h1 { font-size:15pt; margin:0 0 1.2mm; }
.sub { color:#555; font-size:9pt; margin-bottom:2.2mm; }
.tip { background:#f1f8e9; border:0.7pt solid #aed581; border-radius:2mm;
       padding:2mm 3mm; font-size:9pt; color:#33691e; margin:0 0 2.4mm; line-height:1.45; }
.tip b { color:#1b5e20; }
.cols { column-count:2; column-gap:5.5mm; column-rule:0.4pt solid #e2e2e2; }
.alpha { display:block; font-weight:700; font-size:8.1pt; color:#2e7d32;
         background:#eef6ee; border-left:1.1mm solid #66a06b; border-radius:0 0.9mm 0.9mm 0;
         padding:0.3mm 1.5mm; margin:1.4mm 0 0.55mm; break-inside:avoid; break-after:avoid; }
.it { break-inside:avoid; display:flex; align-items:baseline; gap:0.8mm;
      padding:0.32mm 0 0.38mm; border-bottom:0.4pt dotted #c9c9c9; }
.no { flex:none; width:6.4mm; text-align:right; font-size:6.8pt; color:#9a9a9a; }
.ck { flex:none; width:2.7mm; height:2.7mm; border:0.7pt solid #555;
      border-radius:0.3mm; position:relative; top:0.15mm; }
.w { flex:none; font-weight:600; }
.ipa { flex:none; color:#7a7a7a; font-size:7.7pt; }
.sl { flex:none; width:8mm; border-bottom:0.6pt solid #b8b8b8; position:relative; top:-0.3mm; }
.zh { flex:1 1 auto; }
'''

PAGE_CHECK_PAGES = [0, 1, 5, 9, 14, 19]


def esc(s):
    return html.escape(s, quote=False)


def build_html(words):
    out = []
    out.append('<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">')
    out.append('<title>英语雅思词表 · 自测勾叉版</title><style>%s</style></head><body>' % CSS)
    out.append('<h1>英语雅思词表 · 自测勾叉版（进阶）</h1>')
    out.append('<div class="sub">共 %d 词 · 雅思核心词汇（已排除基础词表，两个词表不重复）· 按字母顺序编号 1–%d</div>'
               % (len(words), len(words)))
    out.append('<div class="tip"><b>用法：</b>① 看着英文回忆意思 → 在单词后的横线上写 <b>√</b>（认识）或 <b>×</b>（不认识）；'
               '② 对照后面的中文确认，答对过的词隔几天再遇到、连着两次都对的，在最左边 <b>☐</b> 里打勾；'
               '③ 全部过完后，把打×的词编号发给我，我给您做一对一检测和错题整理。</div>')
    out.append('<div class="cols">')
    cur = ''
    for i, e in enumerate(words, 1):
        letter = e['w'][0].upper()
        if letter != cur:
            cur = letter
            out.append('<div class="alpha">%s</div>' % esc(cur))
        out.append(
            '<div class="it"><span class="no">%d</span><span class="ck"></span>'
            '<span class="w">%s</span><span class="ipa">/%s/</span>'
            '<span class="sl"></span><span class="zh">%s</span></div>'
            % (i, esc(e['w']), esc(e['i']), esc(e['z'])))
    out.append('</div>')
    out.append('</body></html>')
    return '\n'.join(out)


def to_pdf(html_path, pdf_path):
    url = 'file:///' + html_path.replace(os.sep, '/')
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    tmp_profile = os.path.join(os.environ.get('TEMP', r'C:\Windows\Temp'), 'qoder_pdf_prof')
    for exe in BROWSERS:
        if not os.path.exists(exe):
            continue
        cmd = [exe, '--headless', '--disable-gpu',
               '--user-data-dir=' + tmp_profile,
               '--no-pdf-header-footer', '--print-to-pdf-no-header',
               '--print-to-pdf=' + pdf_path, url]
        r = subprocess.run(cmd, capture_output=True, timeout=300)
        size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        print('  [%s] exit=%s size=%s' % (os.path.basename(exe), r.returncode, size))
        if size > 10000:
            return True
    return False


def main():
    words = json.load(io.open(os.path.join(BASE, '_words_ielts_final.json'), encoding='utf-8'))
    print('words:', len(words))

    h_html = os.path.join(BASE, '_ielts.html')
    io.open(h_html, 'w', encoding='utf-8', newline='\n').write(build_html(words))
    print('html written')

    h_pdf = os.path.join(BASE, '_ielts.pdf')
    ok = to_pdf(h_html, h_pdf)
    if not ok:
        print('!! pdf generation failed')
        return
    try:
        import pymupdf
        doc = pymupdf.open(h_pdf)
        print('pages =', doc.page_count, '| sheets(duplex) =', (doc.page_count + 1) // 2)
        for pno in PAGE_CHECK_PAGES:
            if pno < doc.page_count:
                pix = doc[pno].get_pixmap(dpi=110)
                png = os.path.join(BASE, '_chk_ielts_p%d.png' % pno)
                pix.save(png)
                print('rendered', png)
    except Exception as e:
        print('pymupdf check skipped:', e)

    dst = os.path.join(DESK, OUT_PDF_NAME)
    shutil.copyfile(h_pdf, dst)
    print('delivered:', dst)


if __name__ == '__main__':
    main()
