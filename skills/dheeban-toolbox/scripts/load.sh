#!/usr/bin/env bash
# اختبار تحمل: لا تستخدمه على الإنتاج دون إذن المالك
set -e; URL=${1:?URL}; C=${2:-50}; D=${3:-20}
npx -y autocannon@7 -c "$C" -d "$D" --renderStatusCodes "$URL"
