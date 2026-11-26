#!/usr/bin/env bash
# تقليص خط عربي (Fontsource + fonttools) إلى woff2 يحوي العربية واللاتينية الأساسية فقط. جُرّب 2026-11-26.
# الاستعمال: bash fonts-subset.sh cairo 400 [مجلد_الإخراج]   (اسم الحزمة من fontsource.org/fonts)
set -e; N=${1:?اسم الخط}; W=${2:-400}; OUT=${3:-.}; V=/tmp/dheeban-ft; T=$(mktemp -d)
[ -x $V/bin/pyftsubset ] || { python3 -m venv $V && $V/bin/pip -q install fonttools==4.58.4 brotli==1.1.0; }
npm i -s --no-audit --no-fund --prefix "$T" "@fontsource/$N" >/dev/null
F=$(ls "$T/node_modules/@fontsource/$N/files/" | grep -E "arabic-$W-normal.woff2$" | head -1); [ -n "$F" ] || { echo "لا ملف عربي بوزن $W"; exit 1; }
$V/bin/pyftsubset "$T/node_modules/@fontsource/$N/files/$F" --unicodes="U+0600-06FF,U+0750-077F,U+FB50-FDFF,U+FE70-FEFF,U+0020-007E,U+060C,U+061B,U+061F,U+200C-200F" --flavor=woff2 --layout-features='*' --output-file="$OUT/$N-$W-ar.woff2"
ls -l "$T/node_modules/@fontsource/$N/files/$F" "$OUT/$N-$W-ar.woff2" | awk '{print $5, $9}'; rm -rf "$T"
