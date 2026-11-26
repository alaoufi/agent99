#!/usr/bin/env bash
# فحص ترويسات الأمان وSSL لموقع (قراءة فقط، طلب GET واحد + اتصال TLS واحد). الاستعمال: bash headers.sh https://example.com
set -u; URL=${1:?URL}; HOST=$(echo "$URL" | sed -E 's#https?://([^/:]+).*#\1#')
H=$(curl -sS -m 20 -o /dev/null -D - "$URL" | tr -d '\r' | awk 'BEGIN{IGNORECASE=1} /^HTTP\/[0-9.]+ [0-9]+ *$|^HTTP\/2/ {s=$0} {print}' )
echo "$H" | grep -E '^HTTP/' | tail -1; echo "== ترويسات الأمان (✓ موجودة / ✗ مفقودة)"
for k in strict-transport-security content-security-policy x-content-type-options x-frame-options referrer-policy permissions-policy cross-origin-opener-policy cross-origin-resource-policy; do
  v=$(echo "$H" | grep -i "^$k:" | head -1 | cut -c1-110); [ -n "$v" ] && echo "✓ $v" || echo "✗ $k"; done
echo "== تسريب معلومات (يجب ألا تظهر)"; echo "$H" | grep -iE '^(server|x-powered-by|x-aspnet-version):' || echo "لا شيء"
echo "== كوكيز"; echo "$H" | grep -i '^set-cookie:' | sed -E 's/=[^;]+/=***/' || true
echo "== HSTS preload/includeSubDomains"; echo "$H" | grep -i '^strict-transport-security:' | grep -qi includesubdomains && echo "includeSubDomains ✓" || echo "includeSubDomains ✗"
echo "== شهادة SSL (تنبيه: من حاوية ذيبان تُعترض الشهادة بوكيل الخروج، فإن ظهر issuer=Anthropic فالنتيجة لا تخص الموقع؛ افحصها من الخادم أو GitHub Actions)"; echo | openssl s_client -servername "$HOST" -connect "$HOST:443" 2>/dev/null | openssl x509 -noout -issuer -subject -dates 2>/dev/null || echo "تعذّر (قد تمر عبر وكيل الحاوية فتظهر شهادته)"
echo "== إعادة توجيه HTTP→HTTPS"; curl -sS -m 10 -o /dev/null -w "%{http_code} -> %{redirect_url}\n" "http://$HOST/" 2>&1 | tail -1
