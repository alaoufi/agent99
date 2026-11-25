#!/usr/bin/env bash
# مهارات خارجية مفتوحة المصدر يثبّتها ذيبان على مستوى المستخدم (مثبّتة على commit محدد للأمان).
# تحديثها: غيّر الـSHA بعد مراجعة التغييرات. لا تفشل التثبيت أبدًا عند انقطاع الشبكة.
CL="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"; T=$(mktemp -d)
fetch() { # repo sha subdir
  git -C "$T" init -q "$2" 2>/dev/null && git -C "$T/$2" fetch -q --depth 1 "https://github.com/$1" "$2" 2>/dev/null \
    && git -C "$T/$2" checkout -q FETCH_HEAD 2>/dev/null && echo "$T/$2/$3"; }
# 1) frontend-design من Anthropic (MIT/Apache) — تصاميم واجهات احترافية
S=$(fetch anthropics/claude-plugins-official 6985b2d88dc08b4a0d202f5f0301f02e360b9cb1 plugins/frontend-design/skills) && cp -R "$S"/. "$CL/skills/"
# 2) Marketing Skills لـ Corey Haines (MIT) — 53 مهارة تسويق
S=$(fetch coreyhaines31/marketingskills 8fd2fcade2fd6629026e9dfe6d133b55b36968b9 skills) && cp -R "$S"/. "$CL/skills/"
rm -rf "$T"; echo "ذيبان: المهارات الخارجية ثُبّتت في $CL/skills"
