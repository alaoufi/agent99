#!/usr/bin/env bash
# كود وتبعيات وملفات غير مستخدمة (knip). يحتاج typescript كتبعية مرافقة. جُرّب 2026-11-26. الاستعمال: bash deadcode.sh DIR
cd "${1:-.}" || exit 1; npx -y -p knip@5.61.0 -p typescript@5.8.3 knip
