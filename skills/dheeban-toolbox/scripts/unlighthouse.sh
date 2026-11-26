#!/usr/bin/env bash
# فحص كل صفحات موقع بـ Unlighthouse (يزحف على الروابط). جُرّب 2026-11-26 على نسخة محلية.
# للمواقع الحية: اجعل --samples 1 وحدّد --urls لتخفيف الحمل. الاستعمال: bash unlighthouse.sh http://127.0.0.1:8080 [مجلد_الإخراج]
set -e; SITE=${1:?URL}; OUT=${2:-./unlighthouse-out}; mkdir -p "$OUT"; cd "$OUT"
NO_PROXY=127.0.0.1 PUPPETEER_SKIP_DOWNLOAD=1 npx -y unlighthouse@0.16.1 --site "$SITE" --build-static --no-cache --samples 1 \
  --chrome-path /opt/pw-browsers/chromium --disable-dev-tools ${HTTPS_PROXY:+--puppeteer-options "{\"args\":[\"--no-sandbox\",\"--proxy-server=$HTTPS_PROXY\"]}"}
echo "التقرير: $OUT/.unlighthouse/"
