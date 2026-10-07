#!/usr/bin/env bash
# 站点存活检查脚本：逐个访问词表站链接，失败的会重试 3 次；
# 结果追加到 status/site-check.tsv；全部正常退出码 0，有打不开的退出码 1。
# 由 .github/workflows/site-check.yml 每天定时调用；也可本地手动跑。

set -u

cd "$(dirname "$0")/.." || exit 2

OUT="${SITE_CHECK_LOG:-status/site-check.tsv}"

URLS=(
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/"
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/en-basic.html"
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/en-ielts.html"
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/ja.html"
  "https://japanese-vocab-audio-c1gq7yyubx7.qoder.zone/"
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/audio/b/0.mp3"
  "https://japanese-vocab-quiz-c1gq7yyubx7.qoder.zone/audio/e/0.mp3"
  "https://japanese-vocab-audio-c1gq7yyubx7.qoder.zone/audio/j/0.mp3"
)

UA="Mozilla/5.0 (compatible; RAOE-site-check/1.0)"
FAILED=0
DETAIL=""

for u in "${URLS[@]}"; do
  code="000"
  for try in 1 2 3; do
    code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 30 -A "$UA" -L "$u" 2>/dev/null || true)
    code="${code: -3}"
    [ "$code" = "200" ] && break
    if [ "$try" -lt 3 ]; then sleep 10; fi
  done
  if [ "$code" != "200" ]; then
    FAILED=1
    DETAIL="${DETAIL}${u#https://} (${code}); "
  fi
done

NOW=$(TZ=Asia/Shanghai date '+%Y-%m-%d %H:%M')
mkdir -p "$(dirname "$OUT")"
if [ ! -f "$OUT" ]; then
  printf '时间(北京)\t结果\t详情\n' > "$OUT"
fi

if [ "$FAILED" -eq 0 ]; then
  printf '%s\t全部正常\t%d/%d 通过\n' "$NOW" "${#URLS[@]}" "${#URLS[@]}" >> "$OUT"
  echo "[site-check] OK - all ${#URLS[@]} urls healthy at $NOW (Beijing)"
else
  printf '%s\t有打不开的\t%s\n' "$NOW" "$DETAIL" >> "$OUT"
  echo "[site-check] FAIL - $DETAIL"
fi

exit $FAILED
