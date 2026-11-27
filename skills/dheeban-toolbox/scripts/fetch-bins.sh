#!/usr/bin/env bash
# تنزيل أدوات المرحلة 2 بإصدارات مثبتة من GitHub Releases الرسمية مع التحقق من SHA-256.
# الاستخدام: bash fetch-bins.sh [مجلد_الوجهة]  (الافتراضي ~/.dheeb/bin)
# ملاحظة: داخل حاوية ذيبان يمنع المصنِّف تشغيل الثنائيات المنزّلة؛ استخدمه في GitHub Actions أو على الخادم.
set -euo pipefail
DEST="${1:-$HOME/.dheeb/bin}"; mkdir -p "$DEST"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
GH=https://github.com
get() { curl -fsSL --retry 3 -o "$TMP/$2" "$1"; }
check() { echo "$1  $TMP/$2" | sha256sum -c --quiet; }

# Gitleaks v8.28.0 (المجموع من gitleaks_8.28.0_checksums.txt الرسمي)
get "$GH/gitleaks/gitleaks/releases/download/v8.28.0/gitleaks_8.28.0_linux_x64.tar.gz" gl.tgz
check a65b5253807a68ac0cafa4414031fd740aeb55f54fb7e55f386acb52e6a840eb gl.tgz
tar -xzf "$TMP/gl.tgz" -C "$TMP" gitleaks && install -m755 "$TMP/gitleaks" "$DEST/gitleaks"

# hadolint v2.12.0 (المجموع من hadolint-Linux-x86_64.sha256 الرسمي)
get "$GH/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64" hadolint
check 56de6d5e5ec427e17b74fa48d51271c7fc0d61244bf5c90e828aab8362d55010 hadolint
install -m755 "$TMP/hadolint" "$DEST/hadolint"

# k6 v1.0.0 (المجموع من k6-v1.0.0-checksums.txt الرسمي)
get "$GH/grafana/k6/releases/download/v1.0.0/k6-v1.0.0-linux-amd64.tar.gz" k6.tgz
check 5eb2236bc76a3c5cced12aaf0fd76c4b1ceac5ea040c70388a3d272b46595b59 k6.tgz
tar -xzf "$TMP/k6.tgz" -C "$TMP" && install -m755 "$TMP"/k6-v1.0.0-linux-amd64/k6 "$DEST/k6"

# lychee v0.20.1 — الإصدار لا ينشر ملف مجاميع؛ المجموع مسجّل عند أول تنزيل (2026-11-27)
get "$GH/lycheeverse/lychee/releases/download/lychee-v0.20.1/lychee-x86_64-unknown-linux-gnu.tar.gz" ly.tgz
check 1dd08bb064e2114c2c9d0c9009f51577de24e805361d6332162807972d8e9474 ly.tgz
tar -xzf "$TMP/ly.tgz" -C "$TMP" && install -m755 "$(find "$TMP" -type f -name lychee | head -1)" "$DEST/lychee"

echo "ثُبّتت في $DEST: gitleaks hadolint k6 lychee"
