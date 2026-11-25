#!/usr/bin/env bash
# اختبارات ذيب: وحدة (مدخلات خطاف مصطنعة) + تكامل حقيقي عبر claude -p (يتخطى إن لم يتوفر claude).
set -uo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; H="$R/hooks/dheeb_hook.py"
T="$(mktemp -d)"; export DHEEB_STATE="$T/state"; pass=0; fail=0
ok(){ if eval "$2"; then echo "✓ $1"; pass=$((pass+1)); else echo "✗ $1"; fail=$((fail+1)); fi; }
run(){ echo "$2" | python3 "$H" "$1"; }

o=$(run session '{"session_id":"s1","cwd":"/x","source":"startup"}')
ok "SessionStart يحقن السياق" '[[ "$o" == *additionalContext*ذيب* ]]'
o=$(run pre '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"npx playwright install chromium"}}')
ok "منع playwright install" '[[ "$o" == *\"deny\"* ]]'
o=$(run pre '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"ls -la"}}')
ok "أمر عادي يمر بلا تدخل" '[ -z "$o" ]'
seq 1 3000 > "$T/big.txt"
o=$(run pre "{\"session_id\":\"s1\",\"cwd\":\"$T\",\"tool_name\":\"Bash\",\"tool_input\":{\"command\":\"cat big.txt\"}}")
ok "منع cat لملف ضخم" '[[ "$o" == *\"deny\"* ]]'
o=$(run pre '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"grep -rn foo ."}}')
ok "نصيحة grep -r دون منع" '[[ "$o" == *additionalContext* && "$o" != *deny* ]]'
for i in 1 2; do run post '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"git status"}}' >/dev/null; done
o=$(run post '{"session_id":"s1","tool_name":"Bash","tool_input":{"command":"git status"}}')
ok "تنبيه التكرار في المرة الثالثة" '[[ "$o" == *3* && "$o" == *ذيب* ]]'
# سجل مصطنع: رسالة مكررة بالمعرّف نفسه تُحسب مرة واحدة
printf '%s\n' '{"message":{"id":"m1","usage":{"input_tokens":10,"output_tokens":5}}}' \
              '{"message":{"id":"m1","usage":{"input_tokens":10,"output_tokens":5}}}' \
              '{"message":{"id":"m2","usage":{"input_tokens":1,"output_tokens":90000,"cache_read_input_tokens":4000000}}}' > "$T/tr.jsonl"
echo '{"check_every":1}' > "$DHEEB_STATE/policy.json"
o=$(run post "{\"session_id\":\"s2\",\"tool_name\":\"Edit\",\"tool_input\":{},\"transcript_path\":\"$T/tr.jsonl\"}")
ok "تنبيه الاستهلاك المرتفع" '[[ "$o" == *استهلاك* ]]'
run stop "{\"session_id\":\"s2\",\"cwd\":\"/p\",\"transcript_path\":\"$T/tr.jsonl\"}"
ok "Stop يسجل الاستهلاك بلا تكرار (out=90005)" 'grep -q "\"out\": 90005" "$DHEEB_STATE/usage.jsonl"'
o=$(echo 'not json' | python3 "$H" pre; echo "rc=$?")
ok "مدخل تالف لا يكسر الجلسة" '[[ "$o" == *rc=0* ]]'
ok "التقرير يعمل" 'python3 "$R/hooks/dheeb_report.py" | grep "جلسات مسجلة" >/dev/null'
CLAUDE_CONFIG_DIR="$T/cl" DHEEB_STATE="$T/st2" bash "$R/install.sh" >/dev/null && \
CLAUDE_CONFIG_DIR="$T/cl" DHEEB_STATE="$T/st2" bash "$R/install.sh" >/dev/null
ok "التثبيت مكرر بلا ازدواج خطافات" '[ "$(grep -c dheeb_hook "$T/cl/settings.json")" = 4 ]'
ok "--check ينجح" 'CLAUDE_CONFIG_DIR="$T/cl" DHEEB_STATE="$T/st2" bash "$R/install.sh" --check >/dev/null'

# تكامل حقيقي: جلسة claude -p بخطافات ذيب فقط (إعدادات مستقلة، دون لمس ~/.claude)
if command -v claude >/dev/null && [ "${DHEEB_SKIP_E2E:-}" != 1 ]; then
  export DHEEB_STATE="$T/e2e"
  cat > "$T/s.json" <<J
{"hooks":{"SessionStart":[{"matcher":"","hooks":[{"type":"command","command":"python3 $H session"}]}],
 "PreToolUse":[{"matcher":"Bash|Read","hooks":[{"type":"command","command":"python3 $H pre"}]}],
 "PostToolUse":[{"matcher":"","hooks":[{"type":"command","command":"python3 $H post"}]}],
 "Stop":[{"matcher":"","hooks":[{"type":"command","command":"python3 $H stop"}]}]}}
J
  o=$(cd "$T" && timeout 180 claude -p --settings "$T/s.json" --allowedTools Bash --max-turns 4 \
     "شغّل بالأداة Bash الأمر: npx playwright install chromium . ثم أجب بسطر واحد: هل منعك أحد؟ واذكر اسم من منعك. ثم: هل تعرف وكيلًا اسمه ذيب من سياق الجلسة؟ نعم/لا" 2>&1)
  echo "  رد الجلسة: $(echo "$o" | tail -3 | tr '\n' ' ')"
  ok "e2e: الخطاف منع الأمر فعليًا" 'grep -q "\"block\"" "$DHEEB_STATE/events.jsonl"'
  ok "e2e: SessionStart أطلق" 'grep -q "\"session\"" "$DHEEB_STATE/events.jsonl"'
  ok "e2e: Stop سجّل الاستهلاك" '[ -s "$DHEEB_STATE/usage.jsonl" ]'
  ok "e2e: النموذج رأى سياق ذيب" '[[ "$o" == *ذيب* ]]'
fi
echo "النتيجة: $pass نجح، $fail فشل"; rm -rf "$T"; [ $fail = 0 ]
