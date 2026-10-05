# -*- coding: utf-8 -*-
"""开发版注入：给三套自测程序的单词行加"小喇叭"按钮（点按播放 audio/<app>/<序号>.mp3）。
读取现有成品 HTML，写出到 audio_dev/，不改动线上任何文件。"""
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)

SRC = [
    ('b', 'audio/b/', os.path.join(ROOT, 'tools_basic3000', '_app.html'), os.path.join(BASE, 'en-basic.html')),
    ('e', 'audio/e/', os.path.join(ROOT, 'tools_basic3000', '_app_ielts.html'), os.path.join(BASE, 'en-ielts.html')),
    ('j', 'audio/j/', os.path.join(ROOT, 'tools_japanese', '_app_ja.html'), os.path.join(BASE, 'ja.html')),
]

CSS = (
    '.spkbtn{position:relative;display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;'
    'border-radius:50%;border:0;background:#eef2f7;color:#7d8fa4;margin-left:7px;vertical-align:-6px;'
    'cursor:pointer;padding:0;transition:background .12s,color .12s}\n'
    '.spkbtn::after{content:"";position:absolute;top:-4px;right:-8px;bottom:-8px;left:-8px}\n'
    '.spkbtn:hover{background:#e2e8f0;color:#42566d}\n'
    '.spkbtn.on{background:#10b981;color:#fff}\n'
    '.spkbtn svg{display:block}\n'
)

JS_TMPL = """
var AUDIO_DIR = '%s';
var curAudio = null;
function playAudio(i, btn){
  if(curAudio){ try{ curAudio.pause(); }catch(e){} curAudio = null; }
  var a = new Audio(AUDIO_DIR + i + '.mp3');
  curAudio = a;
  if(btn){ btn.classList.add('on'); }
  a.addEventListener('ended', function(){ if(btn){ btn.classList.remove('on'); } if(curAudio === a){ curAudio = null; } });
  a.addEventListener('error', function(){ if(btn){ btn.classList.remove('on'); } });
  var p = a.play();
  if(p && p.catch){ p.catch(function(){ if(btn){ btn.classList.remove('on'); } }); }
}
function spkHTML(i){
  return '<button class="spkbtn" type="button" data-i="' + i + '" aria-label="播放发音"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 5 6 9H3v6h3l5 4z"></path><path d="M15.5 8.5a5 5 0 0 1 0 7"></path></svg></button>';
}
"""


def sub_once(s, old, new, tag):
    c = s.count(old)
    if c != 1:
        raise SystemExit('anchor not unique [%s]: count=%d' % (tag, c))
    return s.replace(old, new)


for app, adir, src, dst in SRC:
    html = open(src, encoding='utf-8').read()

    html = sub_once(html, '</style>', CSS + '</style>', app + ':css')
    html = sub_once(html, 'window.__app = {', JS_TMPL % adir + 'window.__app = {', app + ':js')

    old_click = "  var t = ev.target;\n  var mb = t.closest ? t.closest('.mb') : null;"
    new_click = ("  var t = ev.target;\n"
                 "  var spb = t.closest ? t.closest('.spkbtn') : null;\n"
                 "  if(spb){ playAudio(+spb.getAttribute('data-i'), spb); return; }\n"
                 "  var mb = t.closest ? t.closest('.mb') : null;")
    html = sub_once(html, old_click, new_click, app + ':click')

    old_mark = "  var isNew = !(i in ans);\n  ans[i] = v;\n  if(isNew) order.push(i);\n  save();"
    new_mark = (old_mark + "\n"
                "  playAudio(i, document.querySelector('.spkbtn[data-i=\"' + i + '\"]'));")
    html = sub_once(html, old_mark, new_mark, app + ':markplay')

    if app in ('b', 'e'):
        old_ripa = "'<div class=\"ripa\">' + (en.i ? '/' + en.i + '/' : '') + '</div>'"
        new_ripa = "'<div class=\"ripa\">' + (en.i ? '/' + en.i + '/' : '') + spkHTML(i) + '</div>'"
    else:
        old_ripa = "'<div class=\"ripa\">' + esc(readStr(en)) + '</div>'"
        new_ripa = "'<div class=\"ripa\">' + esc(readStr(en)) + spkHTML(i) + '</div>'"
    html = sub_once(html, old_ripa, new_ripa, app + ':ripa')

    open(dst, 'w', encoding='utf-8').write(html)
    print('%s -> %s  (%d bytes)  [all anchors ok]' % (
        os.path.basename(src), os.path.basename(dst), len(html.encode('utf-8'))), flush=True)
