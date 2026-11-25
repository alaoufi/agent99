#!/usr/bin/env bash
# تثبيت ذيبان على مستوى المستخدم (~/.claude) — آمن للتكرار، لا يعيد تثبيت أي أداة، ولا يمس إعدادات المشاريع.
# الاستعمال: bash install.sh [--check]
set -euo pipefail
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CL="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
ST="${DHEEB_STATE:-$HOME/.dheeb}"

if [ "${1:-}" = "--check" ]; then
  ok=1
  for f in "$ST/bin/dheeb_hook.py" "$CL/agents/dheeban.md" "$CL/skills/dheeban/SKILL.md"; do
    [ -f "$f" ] && echo "✓ $f" || { echo "✗ $f"; ok=0; }
  done
  grep -q dheeb_hook "$CL/settings.json" 2>/dev/null && echo "✓ الخطافات في $CL/settings.json" || { echo "✗ الخطافات"; ok=0; }
  [ $ok = 1 ] && echo "ذيبان مثبّت." || { echo "ذيبان غير مكتمل."; exit 1; }
  exit 0
fi

rm -rf "$CL/skills/dheeb" "$CL/agents/dheeb.md"
mkdir -p "$ST/bin" "$ST/sessions" "$CL/agents" "$CL/skills/dheeban"
install -m 0755 "$SRC/hooks/dheeb_hook.py" "$SRC/hooks/dheeb_report.py" "$ST/bin/"
install -m 0644 "$SRC/agents/dheeban.md" "$CL/agents/dheeban.md"
for s in "$SRC"/skills/*/; do n=$(basename "$s"); mkdir -p "$CL/skills/$n"; cp -R "$s." "$CL/skills/$n/"; done
[ -f "$SRC/memory/MEMORY.md" ] && install -m 0644 "$SRC/memory/MEMORY.md" "$ST/MEMORY.md"
[ -f "$SRC/policy.json" ] && [ ! -f "$ST/policy.json" ] && install -m 0644 "$SRC/policy.json" "$ST/policy.json"
echo "$SRC" > "$ST/source"
[ "${DHEEB_NO_EXTERNAL:-}" = 1 ] || bash "$SRC/bootstrap/external.sh" || true

# دمج الخطافات في إعدادات المستخدم دون حذف أي خطاف آخر (يُزال فقط إدخال ذيبان القديم ثم يُضاف الجديد)
python3 - "$CL/settings.json" "$ST/bin/dheeb_hook.py" <<'PY'
import json, os, sys
path, hook = sys.argv[1], sys.argv[2]
try:
    s = json.load(open(path))
except Exception:
    s = {}
H = s.setdefault("hooks", {})
want = {"SessionStart": ("", "session", 10), "PreToolUse": ("Bash|Read", "pre", 5),
        "PostToolUse": ("", "post", 5), "Stop": ("", "stop", 10)}
for ev, (matcher, arg, to) in want.items():
    groups = [g for g in H.get(ev, []) if not any("dheeb_hook" in (h.get("command") or "") for h in g.get("hooks", []))]
    groups.append({"matcher": matcher, "hooks": [{"type": "command", "command": f"python3 {hook} {arg}", "timeout": to}]})
    H[ev] = groups
os.makedirs(os.path.dirname(path), exist_ok=True)
json.dump(s, open(path, "w"), ensure_ascii=False, indent=2)
PY
echo "ذيبان: ثُبّت في $CL و$ST"
