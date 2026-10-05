# -*- coding: utf-8 -*-
"""组装两个待部署站点文件夹（audio_sites/en、audio_sites/ja），符合 Qoder Sites 平台限制：
  每站文件数 < 10000、总字节 < 50 MiB、单文件 < 50 MiB。
  en: index.html（入口页）+ en-basic.html + en-ielts.html + ja.html（跳转到日语站，保旧链接）+ audio/b + audio/e
  ja: index.html（日语自测程序本体）+ audio/j                                   -> 上线时新建域名
音频由 transcode32.py 生成；本脚本只组装 HTML 并做限制校验，可重复运行。"""
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

HERE = os.path.dirname(os.path.abspath(__file__))   # audio_dev
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'audio_sites')

# 日语站正式地址（2026-10-05 上线创建）：入口页日语卡片与 ja.html 跳转页都指向这里。
JA_URL = 'https://japanese-vocab-audio-c1gq7yyubx7.qoder.zone/'

EXPECT_AUDIO = {'en/audio/b': 3887, 'en/audio/e': 2946, 'ja/audio/j': 3961}
LIMIT_FILES = 10000
LIMIT_BYTES = 50 * 1024 * 1024

HUB = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#10b981">
<title>词汇自测中心</title>
<meta name="description" content="英语基础词汇、英语雅思词汇、日语词汇三套极速刷词自测程序，全部带发音">
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;padding:0}
body{
  font-family:"Microsoft YaHei","PingFang SC",system-ui,-apple-system,"Segoe UI",sans-serif;
  background:#f2f4f7;color:#22303f;
  min-height:100vh;padding:26px 16px 30px;display:flex;justify-content:center;
}
#wrap{width:100%;max-width:560px}
h1{font-size:23px;margin:0 0 6px;color:#17293e;letter-spacing:.5px}
.sub{font-size:13.5px;color:#7d8fa4;margin:0 0 18px}
.card{
  display:flex;align-items:center;gap:14px;background:#fff;border-radius:16px;
  padding:17px 18px;margin-bottom:12px;text-decoration:none;color:inherit;
  box-shadow:0 1px 3px rgba(16,24,40,.07);border-left:5px solid #10b981;
  transition:transform .12s,box-shadow .12s;
}
.card:active{transform:scale(.985)}
.card.blue{border-left-color:#2563eb}
.card.red{border-left-color:#e11d48}
.card .txt{flex:1 1 auto}
.card .name{font-size:17.5px;font-weight:700;color:#17293e;line-height:1.3}
.card .meta{font-size:12.5px;color:#8a97a8;margin-top:4px}
.card .go{
  flex:0 0 auto;font-size:13px;font-weight:700;color:#10b981;background:#ecfdf5;
  border-radius:999px;padding:8px 14px;
}
.card.blue .go{color:#2563eb;background:#eff4ff}
.card.red .go{color:#e11d48;background:#fff1f4}
.tip{font-size:12px;color:#93a1b2;line-height:1.7;margin:16px 4px 0}
</style>
</head>
<body>
<div id="wrap">
  <h1>词汇自测中心</h1>
  <p class="sub">选择一套词表，点「开始」即可刷词；点 ✗ / ✓ 标记，点小喇叭听发音，结果可导出发回。</p>

  <a class="card" href="en-basic.html">
    <div class="txt">
      <div class="name">英语基础词汇</div>
      <div class="meta">3887 词 · 初中高中基础 · 音标 + 发音</div>
    </div>
    <span class="go">开始</span>
  </a>

  <a class="card blue" href="en-ielts.html">
    <div class="txt">
      <div class="name">英语雅思词汇</div>
      <div class="meta">2946 词 · 进阶 · 不含基础词汇 · 带发音</div>
    </div>
    <span class="go">开始</span>
  </a>

  <a class="card red" href="__JA_URL__">
    <div class="txt">
      <div class="name">日语词汇</div>
      <div class="meta">3961 词 · N5N4 + N3 · 假名读音 + 发音</div>
    </div>
    <span class="go">开始</span>
  </a>

  <p class="tip">做题记录保存在你自己手机上，换人换设备互不影响。点小喇叭即可听该词发音。若要像 App 一样使用：在手机浏览器里打开后，用菜单中的「添加到主屏幕」。从微信里打开时，若提示「在浏览器打开」可照做。</p>
</div>
</body>
</html>
'''

JA_REDIRECT = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#10b981">
<meta http-equiv="refresh" content="0; url=__JA_URL__">
<title>日语词汇 · 正在前往新地址</title>
<style>
body{margin:0;font-family:"Microsoft YaHei","PingFang SC",sans-serif;background:#f2f4f7;color:#22303f;
     display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center;padding:20px}
a{color:#10b981}
</style>
</head>
<body>
<div>
  <p>日语词汇自测已搬到新地址，正在跳转…</p>
  <p><a href="__JA_URL__">如果没有自动跳转，点这里</a></p>
</div>
<script>location.replace('__JA_URL__');</script>
</body>
</html>
'''


def copy(src, dst):
    shutil.copyfile(src, dst)
    print('  %s  <-  %s  (%d bytes)' % (os.path.basename(dst), os.path.relpath(src, ROOT), os.path.getsize(dst)))


def check_site(label, folder):
    nfiles = 0
    nbytes = 0
    biggest = 0
    for dirpath, _, filenames in os.walk(folder):
        for fn in filenames:
            if fn.endswith('.tmp'):
                continue
            sz = os.path.getsize(os.path.join(dirpath, fn))
            nfiles += 1
            nbytes += sz
            biggest = max(biggest, sz)
    ok = nfiles < LIMIT_FILES and nbytes < LIMIT_BYTES and biggest < LIMIT_BYTES
    print('[%s] files=%d / 10000   total=%.1f MiB / 50   biggest=%.2f MiB   -> %s' % (
        label, nfiles, nbytes / 1048576, biggest / 1048576, 'OK' if ok else 'OVER LIMIT'))
    return ok


def main():
    en = os.path.join(OUT, 'en')
    ja = os.path.join(OUT, 'ja')
    os.makedirs(en, exist_ok=True)
    os.makedirs(ja, exist_ok=True)

    print('assemble en site:')
    copy(os.path.join(HERE, 'en-basic.html'), os.path.join(en, 'en-basic.html'))
    copy(os.path.join(HERE, 'en-ielts.html'), os.path.join(en, 'en-ielts.html'))
    hub = HUB.replace('__JA_URL__', JA_URL)
    with open(os.path.join(en, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(hub)
    print('  index.html (hub)  (%d bytes)' % len(hub.encode('utf-8')))
    redir = JA_REDIRECT.replace('__JA_URL__', JA_URL)
    with open(os.path.join(en, 'ja.html'), 'w', encoding='utf-8') as f:
        f.write(redir)
    print('  ja.html (redirect -> ja site)  (%d bytes)' % len(redir.encode('utf-8')))

    print('assemble ja site:')
    copy(os.path.join(HERE, 'ja.html'), os.path.join(ja, 'index.html'))

    print('--- limits check ---')
    ok = check_site('en', en) and check_site('ja', ja)

    print('--- audio count check ---')
    for rel, expect in EXPECT_AUDIO.items():
        d = os.path.join(OUT, rel)
        n = len([f for f in os.listdir(d) if f.endswith('.mp3')]) if os.path.isdir(d) else 0
        flag = 'OK' if n == expect else 'NOT READY (%d, transcode still running?)' % n
        print('  %-14s %d / %d  -> %s' % (rel, n, expect, flag))

    if '127.0.0.1' in JA_URL:
        print()
        print('WARNING: 入口页里的日语链接当前为本地测试地址（127.0.0.1:8014/ja/）。')
        print('         上线前必须把脚本顶部 JA_URL 改成日语站正式网址并重新运行本脚本！')
    print()
    print('done. sites root:', OUT)


main()
