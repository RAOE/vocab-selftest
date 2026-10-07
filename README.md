# 词汇自测中心（极速刷词 · 发音版）

给手机浏览器用的单词自测工具：三套词表、每个单词都带发音、点 ✓/✗ 标记时自动朗读该词，做题记录保存在自己手机上。

## 在线体验

<p align="center">
  <img src="assets/公众号二维码-问答小王子-1280.jpg" width="260" alt="公众号「问答小王子」二维码"><br>
  微信扫码关注公众号「问答小王子」，从公众号里进入三套词表，手机在线刷词<br>
  （也可以直接使用下方「线上地址」里的链接）
</p>

## 三套词表

| 程序 | 词数 | 说明 | 文件 |
| --- | --- | --- | --- |
| 英语基础词汇 | 3887 | 初中 + 高中基础词汇，音标 + 发音 | en-basic.html |
| 英语雅思词汇 | 2946 | 进阶词汇（不含基础词，与基础表零重复） | en-ielts.html |
| 日语词汇 | 3961 | N5/N4 + N3 常用词，假名读音 + 发音 | ja/index.html |

## 线上地址

- 入口页（选词表）：<https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/>
- 英语基础词汇：<https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/en-basic.html>
- 英语雅思词汇：<https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/en-ielts.html>
- 日语词汇：<https://japanese-vocab-audio-c1gq7yyubx7.qoder.zone/>

微信里已发过的旧链接继续有效：日语旧链接指向的 ja.html 会自动跳转到新的日语站。

## 使用方式

- 打开网址 → 选词表 → 点「开始」。
- 看单词想意思，认识点 ✓、不认识点 ✗；也可以用键盘：`→` = ✓，`←` = ✗，`回车` = 下一组。
- **点 ✓/✗（含快捷键）会自动朗读这个词**；想反复听就点小喇叭。
- 每 7 个词一组；答完后有统计和「重做错词」；记录存在浏览器本地，换人换设备互不影响，可导出结果。
- 手机浏览器里用菜单「添加到主屏幕」，可以像 App 一样打开。

## 目录结构

| 目录 | 内容 |
| --- | --- |
| `audio_sites/en/` | 英语站部署文件：入口页 index.html、两套英语程序、ja.html（跳转日语站）、audio/b + audio/e 发音 |
| `audio_sites/ja/` | 日语站部署文件：index.html（日语程序）、audio/j 发音 |
| `audio_dev/` | 开发脚本与带发音的 HTML：音频生成/转码、发音注入、站点组装 |
| `tools_basic3000/` | 英语两套词表的数据与生成脚本（清洗、程序生成、打印版 PDF 生成） |
| `tools_japanese/` | 日语词表数据与程序生成脚本 |
| `dist/` | 早期无发音版本（保留备用） |
| `docs/` | 打印版 PDF：英语基础词表-自测勾叉版（36 页，双面 18 张）、英语雅思词表-自测勾叉版（32 页，双面 16 张） |
| `make_site.py` | 组装无发音版 dist 的旧脚本 |

## 本地预览

音频通过相对路径加载，建议用本地服务器（在 `audio_sites` 目录下执行）：

```
python -m http.server 8014
```

然后浏览器打开 <http://localhost:8014/en/>（英语站）或 <http://localhost:8014/ja/>（日语站）。

## 音频说明

- 每个词一个 mp3：`audio/b|e|j/序号.mp3`（序号 = 词表顺序，从 0 开始）。
- 由微软 Edge 在线语音合成批量生成（英文 en-GB-SoniaNeural 英式女声；日语 ja-JP-NanamiNeural 女声），生成脚本 `audio_dev/gen_audio.py`。
- 站点内音频为 32 kbps 单声道（`audio_dev/transcode32.py` 转码），这是为满足部署平台 50 MiB 体积限制；母版更高码率未包含在本仓库，可用脚本重新生成。

## 重新部署（平台限制说明）

部署平台限制：**单站点 < 10000 个文件、总体积 < 50 MiB**。全部音频约 1.08 万个文件 / 61 MiB，因此拆成两个站点：

- **英语站** = `audio_sites/en`（6837 个文件、34.9 MiB）
- **日语站** = `audio_sites/ja`（3962 个文件、26.3 MiB）

构建链（按顺序运行即可重复整个流程）：

1. `tools_basic3000/make_app.py`、`make_app_ielts.py`、`tools_japanese/make_app_ja.py` —— 生成三个无发音程序
2. `audio_dev/gen_audio.py` —— 批量合成发音 mp3
3. `audio_dev/build_audio_apps.py` —— 把发音功能与"标记自动朗读"注入三个程序
4. `audio_dev/transcode32.py` —— 转码 32 kbps
5. `audio_dev/make_audio_sites.py` —— 组装两个站点并校验平台限制（脚本顶部 `JA_URL` 为日语站正式地址）

## 数据来源

词表由公开开源数据整理而成，仅供个人学习使用：

- 英语基础词表：基于开源词表 english-vocabulary（junior/senior）整理
- 英语雅思词表：从开放词典 ECDICT（MIT 许可）筛选整理
- 日语词表：基于开源日语词表数据整理

## 更新记录

- 2026-10-07：README 顶部新增公众号「问答小王子」二维码（微信扫码在线体验），原图两个尺寸存于 `assets/`。
- 2026-10-05：加入"标记（✓/✗/快捷键）自动播放发音"；整理本仓库并推送到 GitHub；两个发音版站点上线。
