# -*- coding: utf-8 -*-
r"""生成《日语词表-自测程序.html》：极速刷词风格（一组7词列表、点击显示中文、下一组），点认识/不认识自动记录、可续测、可导出结果。
输出：tools_japanese/_app_ja.html、桌面\日语词表-自测程序.html、项目 dist\index.html（用于发布）"""
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))

words = json.load(open(os.path.join(BASE, '_words_ja_final.json'), encoding='utf-8'))
slim = [{'w': e['w'], 'i': e.get('i', ''), 'p': e.get('p', ''), 'z': e.get('z', '')} for e in words]
data_js = json.dumps(slim, ensure_ascii=False, separators=(',', ':'))
data_js = data_js.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')

TEMPLATE = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<meta name="theme-color" content="#10b981">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<title>日语词表 · 自测程序</title>
<style>
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
[hidden]{display:none!important}
html,body{margin:0;padding:0}
body{
  font-family:"Microsoft YaHei","PingFang SC",system-ui,-apple-system,"Segoe UI",sans-serif;
  background:#f2f4f7;color:#22303f;display:flex;justify-content:center;
  padding:12px 12px 22px;-webkit-user-select:none;user-select:none;
}
#app{width:100%;max-width:680px;display:flex;flex-direction:column;gap:10px}
#testView{display:flex;flex-direction:column;gap:9px}
.hcard{background:#fff;border-radius:16px;padding:12px 16px 13px;box-shadow:0 1px 3px rgba(16,24,40,.07)}
.hrow{display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap}
.title{font-size:15px;font-weight:700;color:#37495e}
.tools{display:flex;gap:6px}
.tbtn{font-size:12.5px;color:#5b6c80;background:#f2f4f7;border-radius:999px;padding:7px 13px;font-weight:600;border:0;cursor:pointer;font-family:inherit}
.tbtn:hover{background:#e8ecf1}
.tbtn.red{color:#dc2626}
.hrow2{display:flex;justify-content:space-between;align-items:flex-end;margin-top:11px}
.bignum b{font-size:33px;font-weight:800;color:#17293e;line-height:1;display:block}
.bignum span{font-size:11.5px;color:#9aa5b4;display:block;margin-top:3px}
.hright{text-align:right}
.hright .main{font-size:14.5px;color:#5b6c80;font-weight:600}
.hright .main b{color:#17293e;font-weight:700}
.hright .sub{font-size:11.5px;color:#9aa5b4;margin-top:3px}
.barwrap{height:5px;background:#eef1f5;border-radius:4px;overflow:hidden;margin-top:10px}
#bar{height:100%;width:0;background:#10b981;border-radius:4px;transition:width .2s}
#list{display:flex;flex-direction:column;gap:8px}
.wrow{background:#fff;border-radius:14px;box-shadow:0 1px 3px rgba(16,24,40,.07);display:flex;align-items:center;gap:12px;padding:10px 14px;border:1.5px solid transparent;transition:background .15s,border-color .15s}
.wrow.ok{background:#f0fdf6;border-color:#a7f3d0}
.wrow.no{background:#fef2f2;border-color:#fecaca}
.wrow.flash{animation:flashrow .9s ease}
@keyframes flashrow{0%,55%{box-shadow:0 0 0 3px rgba(245,158,11,.6)}100%{box-shadow:0 1px 3px rgba(16,24,40,.07)}}
.rno{flex:0 0 16px;font-size:12.5px;color:#9aa5b4;text-align:center;font-weight:600}
.wordbox{flex:0 0 auto;min-width:114px;max-width:46%;cursor:pointer}
.rw{font-size:19px;font-weight:700;color:#17293e;line-height:1.22;word-break:break-word}
.ripa{font-size:12.5px;color:#94a3b8;font-family:"Yu Gothic","Hiragino Sans","Noto Sans JP","Segoe UI",Arial,sans-serif;margin-top:3px}
.meanbox{flex:1 1 auto;min-width:88px;display:flex;align-items:center;cursor:pointer}
.meanbox .hint{display:flex;align-items:center;justify-content:center;width:100%;height:38px;background:#f1f3f6;border-radius:10px;color:#9aa5b4;font-size:13px;letter-spacing:1px}
.meanbox .zh{font-size:14px;color:#33475e;line-height:1.45;padding-left:4px}
.markbtns{display:flex;gap:8px;flex:0 0 auto}
.mb{position:relative;width:38px;height:38px;border-radius:50%;border:1.5px solid #e2e8f0;background:#fff;color:#b3bfcc;font-size:15px;font-weight:700;display:flex;align-items:center;justify-content:center;cursor:pointer;font-family:inherit;transition:background .12s,border-color .12s,color .12s;touch-action:manipulation}
.mb::after{content:'';position:absolute;top:-6px;bottom:-6px;left:0;right:0}
.mb.myes:hover{border-color:#10b981;color:#10b981}
.mb.mno:hover{border-color:#ef4444;color:#ef4444}
.mb.myes.on{background:#10b981;border-color:#10b981;color:#fff}
.mb.mno.on{background:#ef4444;border-color:#ef4444;color:#fff}
.hints{text-align:center;font-size:12px;color:#9aa9bb;margin-top:1px}
@media(hover:none){.hints{display:none}}
.jumprow{display:flex;justify-content:center;align-items:center;gap:6px;font-size:12.5px;color:#8a97a8}
.jinput{width:78px;height:32px;border:1.5px solid #dbe3ec;border-radius:9px;background:#fff;color:#22303f;font-size:16px;font-family:inherit;text-align:center;padding:0 6px;margin:0}
.jinput:focus{outline:none;border-color:#10b981}
.jinput::-webkit-outer-spin-button,.jinput::-webkit-inner-spin-button{-webkit-appearance:none;margin:0}
.jbtn{position:relative;height:32px;border:0;border-radius:9px;background:#eef2f7;color:#42566d;font-size:13px;font-weight:700;padding:0 13px;cursor:pointer;font-family:inherit;touch-action:manipulation;transition:background .12s}
.jbtn::after{content:'';position:absolute;top:-6px;bottom:-6px;left:0;right:0}
.jbtn:hover{background:#e2e8f0}
.jbtn:active{transform:scale(.97)}
.nextbtn{width:100%;height:56px;border-radius:999px;background:#10b981;color:#fff;font-size:17px;font-weight:700;border:0;cursor:pointer;font-family:inherit;box-shadow:0 6px 16px rgba(16,185,129,.28);transition:background .15s,transform .05s;touch-action:manipulation}
.nextbtn:hover{background:#0ea371}
.nextbtn:active{transform:scale(.985)}
.navrow{display:flex;gap:10px;align-items:stretch}
.navrow .nextbtn{flex:1 1 auto;width:auto;min-width:0}
.prevbtn{flex:0 0 108px;height:56px;border-radius:999px;background:#fff;color:#42566d;font-size:15px;font-weight:700;border:1.5px solid #dbe3ec;cursor:pointer;font-family:inherit;box-shadow:0 4px 12px rgba(16,24,40,.06);transition:background .15s,transform .05s,opacity .15s;touch-action:manipulation}
.prevbtn:hover{background:#f4f7fa}
.prevbtn:active{transform:scale(.985)}
.prevbtn:disabled{opacity:.4;cursor:default;background:#f6f8fb;box-shadow:none}
@media (max-width:430px){
  .wrow{gap:9px;padding:9px 11px}
  .wordbox{flex:0 1 auto;min-width:80px}
  .meanbox{min-width:64px}
  .rw{font-size:17px}
  .mb{width:34px;height:34px}
  .bignum b{font-size:29px}
}
.dtitle{margin:6px 2px 0;font-size:19px;color:#22344a}
.bigstats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
@media (max-width:560px){.bigstats{grid-template-columns:repeat(2,1fr)}}
.stat{background:#fff;border-radius:14px;padding:14px 8px;text-align:center;box-shadow:0 1px 3px rgba(16,24,40,.07)}
.stat b{display:block;font-size:clamp(20px,5vw,26px);color:#2c3e52}
.stat span{font-size:12.5px;color:#7d8fa4}
.stat.k b{color:#10b981}
.stat.u b{color:#dc2626}
.donebtns{display:flex;gap:10px;flex-wrap:wrap}
.donebtns button{flex:1 1 150px;min-height:52px;font-size:15px;border:0;border-radius:14px;cursor:pointer;font-weight:700;font-family:inherit;transition:background .12s,transform .05s}
.donebtns button:active{transform:scale(.98)}
#bExport{background:#10b981;color:#fff}
#bExport:hover{background:#0ea371}
#bCopy{background:#1565c0;color:#fff}
#bCopy:hover{background:#0d47a1}
.donebtns .plain{background:#fff;color:#42566d;box-shadow:0 1px 3px rgba(16,24,40,.07)}
.donebtns .plain:hover{background:#f4f7fb}
#bReset2{color:#dc2626}
.tip{font-size:12.5px;color:#7d8fa4;line-height:1.6;margin:2px 2px 0}
.listhead{font-size:15px;font-weight:700;color:#37495e;margin:4px 2px 0}
.unklist{background:#fff;border-radius:14px;padding:8px 6px;box-shadow:0 1px 3px rgba(16,24,40,.07);max-height:44vh;overflow:auto}
.urow{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;padding:7px 10px;border-radius:8px;font-size:14px;cursor:pointer;transition:background .12s}
.urow:nth-child(odd){background:#f7f9fc}
.urow:hover{background:#eef4fb}
.urow .uno{color:#a3b0c0;font-size:12px;min-width:46px;text-align:right}
.urow .uw{font-weight:700;color:#22344a}
.urow .ui{color:#8a97a8;font-size:13px;font-family:"Yu Gothic","Hiragino Sans","Noto Sans JP","Segoe UI",Arial,sans-serif}
.urow .uz{color:#4a5d73;margin-left:auto;text-align:right;max-width:46%}
#toast{position:fixed;left:50%;bottom:26px;transform:translateX(-50%) translateY(10px);background:rgba(23,41,62,.92);color:#fff;padding:10px 18px;border-radius:10px;font-size:14px;opacity:0;transition:.2s;pointer-events:none;z-index:99;max-width:86vw;text-align:center}
#toast.on{opacity:1;transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>
<div id="app">

  <div id="testView">
    <header class="hcard">
      <div class="hrow">
        <span class="title">日语词表 · 自测</span>
        <span class="tools">
          <button id="bUndo" class="tbtn">撤销</button>
          <button id="bResult" class="tbtn">结果</button>
          <button id="bReset" class="tbtn red">清空</button>
        </span>
      </div>
      <div class="hrow2">
        <div class="bignum"><b id="sUnknown">0</b><span>不认识的词</span></div>
        <div class="hright">
          <div class="main">已答 <b id="sDone">0</b> / <b id="sTotal">0</b></div>
          <div class="sub" id="sRateLine">认识率 –</div>
        </div>
      </div>
      <div class="barwrap"><div id="bar"></div></div>
    </header>

    <div id="list"></div>

    <div class="hints">键盘：← 标不认识 ｜ → 标认识 ｜ Enter 下一组 ｜ Backspace 撤销</div>

    <div class="jumprow">
      <span>跳到第</span>
      <input id="jumpI" class="jinput" type="number" min="1" inputmode="numeric" aria-label="词号">
      <span>个词</span>
      <button id="jumpB" class="jbtn" type="button">跳转</button>
    </div>

    <div class="navrow">
      <button id="bPrev" class="prevbtn" disabled>上一组</button>
      <button id="bNext" class="nextbtn">下一组</button>
    </div>
  </div>

  <div id="doneView" hidden>
    <h2 class="dtitle">自测结果</h2>
    <div class="bigstats">
      <div class="stat"><b id="dTotal">0</b><span>总词数</span></div>
      <div class="stat k"><b id="dKnown">0</b><span>✓ 认识</span></div>
      <div class="stat u"><b id="dUnknown">0</b><span>✗ 不认识</span></div>
      <div class="stat"><b id="dRate">–</b><span>认识率</span></div>
    </div>
    <div class="donebtns">
      <button id="bExport">导出结果文件</button>
      <button id="bCopy">复制结果</button>
      <button id="bBack" class="plain">继续自测</button>
      <button id="bReset2" class="plain">清空重来</button>
    </div>
    <p class="tip">「导出结果文件」会把 txt 保存到「下载」文件夹（文件名：日语自测结果_日期.txt），把它发给我即可；也可以点「复制结果」，直接在聊天里粘贴给我。手机上可以点浏览器菜单里的「添加到主屏幕」，以后像 App 一样一键打开。不用全部做完，累了随时点「结果」导出。</p>
    <div class="listhead" id="dUnkTitle">不认识的词</div>
    <div id="unkList" class="unklist"></div>
  </div>

</div>
<div id="toast"></div>
<script>
(function(){
'use strict';
var DATA = __DATA__;
var KEY = 'vocab_selftest_ja_v1';
var TOTAL = DATA.length;
var GS = 7;
var lastGroup = Math.ceil(TOTAL / GS) - 1;
var ans = {}, order = [], revealed = {};
var group = 0, advTimer = null, flashIdx = -1;

function $(id){ return document.getElementById(id); }
function esc(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function readStr(e){
  var s = e.i || '';
  if(e.p){ s = s ? (s + ' ' + e.p) : e.p; }
  return s;
}

function load(){
  try{
    var raw = localStorage.getItem(KEY);
    if(!raw) return;
    var st = JSON.parse(raw);
    if(!st || st.v !== 1 || !st.ans || typeof st.ans !== 'object' || !Array.isArray(st.order)) return;
    var seen = {}, ca = {}, co = [];
    st.order.forEach(function(k){
      if(typeof k === 'number' && k >= 0 && k < TOTAL && (k in st.ans) && !(k in seen)){
        seen[k] = 1; ca[k] = st.ans[k] ? 1 : 0; co.push(k);
      }
    });
    ans = ca; order = co;
  }catch(e){}
}
function save(){
  try{ localStorage.setItem(KEY, JSON.stringify({v:1, ans:ans, order:order})); }catch(e){}
}
function counts(){
  var k = 0, u = 0;
  for(var key in ans){ if(ans[key] === 1) k++; else u++; }
  return {k:k, u:u, a:k+u};
}
function firstUnanswered(){
  for(var i = 0; i < TOTAL; i++){ if(!(i in ans)) return i; }
  return -1;
}
function groupOf(i){ return Math.floor(i / GS); }
function groupComplete(g){
  var s = g * GS, e = Math.min(s + GS, TOTAL), i;
  for(i = s; i < e; i++){ if(!(i in ans)) return false; }
  return true;
}
function fmtRate(c){ return c.a ? Math.round(c.k * 1000 / c.a) / 10 + '%' : '–'; }

function renderHeader(){
  var c = counts();
  $('sUnknown').textContent = c.u;
  $('sDone').textContent = c.a;
  $('sTotal').textContent = TOTAL;
  $('sRateLine').textContent = '认识率 ' + fmtRate(c);
  $('bar').style.width = (c.a * 100 / TOTAL) + '%';
  $('bNext').textContent = group >= lastGroup ? '查看结果' : '下一组';
  $('bPrev').disabled = group <= 0;
}

function meanHTML(i){
  return revealed[i]
    ? '<span class="zh">' + esc(DATA[i].z) + '</span>'
    : '<span class="hint">点击显示</span>';
}

function renderList(){
  var s = group * GS, e = Math.min(s + GS, TOTAL), out = [], i, en;
  for(i = s; i < e; i++){
    en = DATA[i];
    out.push(
      '<div class="wrow' + (ans[i] === 1 ? ' ok' : ans[i] === 0 ? ' no' : '') + '" id="row-' + i + '">'
      + '<span class="rno">' + (i - s + 1) + '</span>'
      + '<div class="wordbox" data-i="' + i + '">'
      +   '<div class="rw">' + esc(en.w) + '</div>'
      +   '<div class="ripa">' + esc(readStr(en)) + '</div>'
      + '</div>'
      + '<div class="meanbox" data-i="' + i + '">' + meanHTML(i) + '</div>'
      + '<div class="markbtns">'
      +   '<button class="mb mno' + (ans[i] === 0 ? ' on' : '') + '" data-i="' + i + '" data-v="0">✗</button>'
      +   '<button class="mb myes' + (ans[i] === 1 ? ' on' : '') + '" data-i="' + i + '" data-v="1">✓</button>'
      + '</div>'
      + '</div>');
  }
  $('list').innerHTML = out.join('');
  if(flashIdx >= 0){
    var r = $('row-' + flashIdx);
    if(r){ r.classList.add('flash'); r.scrollIntoView({block:'center'}); }
    flashIdx = -1;
  }
}

function gotoGroup(g, flashI){
  clearTimeout(advTimer);
  g = Math.max(0, Math.min(g, lastGroup));
  group = g;
  if(typeof flashI === 'number') flashIdx = flashI;
  renderHeader();
  renderList();
  window.scrollTo(0, 0);
}

function toggleReveal(i){
  revealed[i] = !revealed[i];
  var box = document.querySelector('.meanbox[data-i="' + i + '"]');
  if(box) box.innerHTML = meanHTML(i);
}

function mark(i, v){
  if(ans[i] === v) return;
  var isNew = !(i in ans);
  ans[i] = v;
  if(isNew) order.push(i);
  save();
  var row = $('row-' + i);
  if(row){
    row.classList.remove('ok','no');
    row.classList.add(v === 1 ? 'ok' : 'no');
    row.querySelector('.myes').classList.toggle('on', v === 1);
    row.querySelector('.mno').classList.toggle('on', v === 0);
  }
  renderHeader();
  if(isNew && groupComplete(group)){
    clearTimeout(advTimer);
    advTimer = setTimeout(function(){
      if(counts().a >= TOTAL || group >= lastGroup){ showDone(); return; }
      gotoGroup(group + 1);
    }, 380);
  }
}

function undo(){
  if(!order.length) return;
  clearTimeout(advTimer);
  var last = order.pop();
  delete ans[last];
  revealed[last] = 1;
  save();
  hideDone();
  gotoGroup(groupOf(last), last);
}

function nextClick(){
  clearTimeout(advTimer);
  if(group >= lastGroup){ showDone(); return; }
  gotoGroup(group + 1);
}

function prevClick(){
  if(group <= 0) return;
  clearTimeout(advTimer);
  gotoGroup(group - 1);
}

function jumpGo(){
  var v = parseInt($('jumpI').value, 10);
  if(!(v >= 1 && v <= TOTAL)){ toast('请输入 1–' + TOTAL + ' 之间的词号'); return; }
  hideDone();
  $('jumpI').blur();
  gotoGroup(groupOf(v - 1), v - 1);
}

function reset(){
  if(!confirm('确定清空全部记录，重新开始吗？')) return;
  clearTimeout(advTimer);
  ans = {}; order = []; revealed = {};
  save();
  hideDone();
  gotoGroup(0);
}

function backToTest(){
  hideDone();
  var fu = firstUnanswered();
  if(fu >= 0) gotoGroup(groupOf(fu));
  else { renderHeader(); renderList(); }
}

function showDone(){
  clearTimeout(advTimer);
  var c = counts();
  $('dTotal').textContent = TOTAL;
  $('dKnown').textContent = c.k;
  $('dUnknown').textContent = c.u;
  $('dRate').textContent = fmtRate(c);
  var parts = [], i, e;
  for(i = 0; i < TOTAL; i++){
    if(ans[i] === 0){
      e = DATA[i];
      parts.push('<div class="urow" data-i="' + i + '"><span class="uno">#' + (i + 1) + '</span><span class="uw">' + esc(e.w) + '</span><span class="ui">' + esc(readStr(e)) + '</span><span class="uz">' + esc(e.z) + '</span></div>');
    }
  }
  $('unkList').innerHTML = parts.length ? parts.join('') : '<div class="urow"><span class="uz">（没有不认识的词）</span></div>';
  $('dUnkTitle').textContent = c.u === 0 ? '不认识的词' : '不认识的词（' + c.u + ' 个）· 点词条可直接跳转';
  $('bBack').textContent = c.a < TOTAL ? '继续自测（还有 ' + (TOTAL - c.a) + ' 个）' : '返回自测';
  $('testView').hidden = true;
  $('doneView').hidden = false;
  window.scrollTo(0, 0);
}
function hideDone(){
  $('doneView').hidden = true;
  $('testView').hidden = false;
}

function pad(n){ return (n < 10 ? '0' : '') + n; }
function todayStr(){
  var d = new Date();
  return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
}

function exportText(){
  var c = counts(), lines = [], i, e, ws = [];
  lines.push('日语词表 自测结果');
  lines.push('日期: ' + todayStr());
  lines.push('总词数: ' + TOTAL);
  lines.push('已答: ' + c.a + '   未答: ' + (TOTAL - c.a));
  lines.push('认识: ' + c.k + '   不认识: ' + c.u + '   认识率: ' + fmtRate(c));
  lines.push('');
  lines.push('== 不认识的词（' + c.u + ' 个）==');
  for(i = 0; i < TOTAL; i++){
    if(ans[i] === 0){
      e = DATA[i];
      lines.push('#' + (i + 1) + '\t' + e.w + '\t' + readStr(e) + '\t' + e.z);
    }
  }
  if(c.u === 0) lines.push('（无）');
  lines.push('');
  lines.push('== 认识的词（' + c.k + ' 个，仅单词）==');
  for(i = 0; i < TOTAL; i++){ if(ans[i] === 1) ws.push(DATA[i].w); }
  if(!ws.length) lines.push('（无）');
  for(i = 0; i < ws.length; i += 12) lines.push(ws.slice(i, i + 12).join(' '));
  return lines.join('\n');
}

function download(){
  var text = exportText();
  var blob = new Blob([text], {type:'text/plain;charset=utf-8'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = '日语自测结果_' + todayStr() + '.txt';
  document.body.appendChild(a);
  a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 2000);
  toast('已导出到「下载」文件夹，把文件发给我即可');
}

var toastTimer = null;
function toast(msg){
  var t = $('toast');
  t.textContent = msg;
  t.classList.add('on');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function(){ t.classList.remove('on'); }, 1800);
}

function copyText(){
  var text = exportText();
  function ok(){ toast('已复制，直接在聊天里粘贴发给我即可'); }
  function fallback(){
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try{ document.execCommand('copy'); ok(); }catch(e){ toast('复制失败，请改用「导出结果文件」'); }
    ta.remove();
  }
  if(navigator.clipboard && navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(ok, fallback);
  }else{
    fallback();
  }
}

$('bUndo').onclick = undo;
$('bResult').onclick = showDone;
$('bReset').onclick = reset;
$('bNext').onclick = nextClick;
$('bPrev').onclick = prevClick;
$('jumpB').onclick = jumpGo;
$('jumpI').addEventListener('keydown', function(ev){ if(ev.key === 'Enter'){ ev.preventDefault(); jumpGo(); } });
$('bExport').onclick = download;
$('bCopy').onclick = copyText;
$('bBack').onclick = backToTest;
$('bReset2').onclick = reset;

$('list').addEventListener('click', function(ev){
  var t = ev.target;
  var mb = t.closest ? t.closest('.mb') : null;
  if(mb){ mark(+mb.getAttribute('data-i'), +mb.getAttribute('data-v')); return; }
  var wb = t.closest('.wordbox') || t.closest('.meanbox');
  if(wb) toggleReveal(+wb.getAttribute('data-i'));
});

$('unkList').addEventListener('click', function(ev){
  var t = ev.target;
  var ur = t.closest ? t.closest('.urow') : null;
  if(!ur || !ur.hasAttribute('data-i')) return;
  var i = +ur.getAttribute('data-i');
  hideDone();
  gotoGroup(groupOf(i), i);
});

document.addEventListener('keydown', function(ev){
  if(ev.target && (ev.target.tagName === 'INPUT' || ev.target.tagName === 'TEXTAREA')) return;
  if(!$('doneView').hidden){
    if(ev.key === 'Escape') backToTest();
    return;
  }
  if(ev.key === 'ArrowLeft' || ev.key === 'ArrowRight'){
    ev.preventDefault();
    var s = group * GS, e = Math.min(s + GS, TOTAL), i, t = -1;
    for(i = s; i < e; i++){ if(!(i in ans)){ t = i; break; } }
    if(t >= 0) mark(t, ev.key === 'ArrowRight' ? 1 : 0);
    else if(ev.key === 'ArrowRight') nextClick();
    return;
  }
  if(ev.key === 'Enter'){ ev.preventDefault(); nextClick(); return; }
  if(ev.key === 'Backspace'){ ev.preventDefault(); undo(); return; }
});

window.__app = {
  getState: function(){ var c = counts(); return {total:TOTAL, answered:c.a, known:c.k, unknown:c.u, next:firstUnanswered(), group:group}; },
  mark: mark,
  undo: undo,
  gotoGroup: gotoGroup,
  nextClick: nextClick,
  prevClick: prevClick,
  jumpGo: jumpGo,
  toggleReveal: toggleReveal,
  showDone: showDone,
  backToTest: backToTest,
  exportText: exportText,
  resetNow: function(){ clearTimeout(advTimer); ans = {}; order = []; revealed = {}; save(); hideDone(); gotoGroup(0); },
  fillRest: function(v){
    var i;
    while((i = firstUnanswered()) >= 0){ ans[i] = v; order.push(i); }
    save();
    if(firstUnanswered() < 0){ renderHeader(); showDone(); }
    else { renderHeader(); renderList(); }
  }
};

load();
(function init(){
  $('jumpI').placeholder = '1–' + TOTAL;
  var fu = firstUnanswered();
  if(fu >= 0){ group = groupOf(fu); renderHeader(); renderList(); }
  else { renderHeader(); showDone(); }
})();
})();
</script>
</body>
</html>
'''

html = TEMPLATE.replace('__DATA__', data_js)

out = os.path.join(BASE, '_app_ja.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
dst = os.path.join(desktop, '日语词表-自测程序.html')
shutil.copyfile(out, dst)

dist = os.path.normpath(os.path.join(BASE, '..', 'dist'))
os.makedirs(dist, exist_ok=True)
site = os.path.join(dist, 'ja.html')
shutil.copyfile(out, site)

print('words:', len(slim))
print('html bytes:', len(html.encode('utf-8')))
print('desktop:', dst, os.path.exists(dst))
print('site dist:', site, os.path.exists(site))
