#!/usr/bin/env bash
# فحص ساكن لكود أندرويد/iOS بـ mobsfscan (مصدر لا APK). جُرّب 2026-11-26. الاستعمال: bash mobsf.sh DIR  → mobsf.json + ملخص
set -e; V=/tmp/dheeban-ft; [ -x $V/bin/mobsfscan ] || { python3 -m venv $V && $V/bin/pip -q install mobsfscan==0.4.5; }
$V/bin/mobsfscan --json -o mobsf.json "${1:-.}" >/dev/null 2>&1 || true
python3 - <<'P'
import json; d=json.load(open('mobsf.json')); r=d.get('results',{})
for k,v in r.items(): print(v['metadata']['severity'], k, '-', v['metadata']['description'][:90], f"({len(v.get('files',[]))} ملف)")
print('المجموع:', len(r))
P
