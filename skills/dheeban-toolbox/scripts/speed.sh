#!/usr/bin/env bash
# قياس Lighthouse: الأداء والوصولية وSEO وأفضل الممارسات
set -e; URL=${1:?URL}; OUT=${2:-.}
npx -y lighthouse@12 "$URL" --chrome-path=/opt/pw-browsers/chromium --chrome-flags="--headless --no-sandbox" \
  --only-categories=performance,accessibility,seo,best-practices --output=json --output=html \
  --output-path="$OUT/lh" --quiet
python3 -c "import json;d=json.load(open('$OUT/lh.report.json'));print({k:v['score'] for k,v in d['categories'].items()});a=d['audits'];[print(k,a[k]['displayValue']) for k in ('first-contentful-paint','largest-contentful-paint','total-blocking-time','cumulative-layout-shift') if k in a]"
echo "التقرير الكامل: $OUT/lh.report.html"
