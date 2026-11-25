#!/usr/bin/env bash
# فحص أمني خفيف لمجلد مشروع: تبعيات + أسرار + semgrep بقواعد محلية إن وُجدت
DIR=${1:-.}; cd "$DIR" || exit 1
[ -f package-lock.json ] && { echo "== npm audit"; npm audit --omit=dev 2>/dev/null | tail -5; }
[ -f pnpm-lock.yaml ] && { echo "== pnpm audit"; npx -y pnpm@9 audit --prod 2>/dev/null | tail -5; }
echo "== أسرار مكشوفة (secretlint)"; RC=$(mktemp); echo '{"rules":[{"id":"@secretlint/secretlint-rule-preset-recommend"}]}' > "$RC"
IG=""; [ -f .gitignore ] && IG="--secretlintignore .gitignore"
npx -y -p secretlint@9 -p @secretlint/secretlint-rule-preset-recommend@9 secretlint --secretlintrc "$RC" $IG "**/*" 2>&1 | tail -15; rm -f "$RC"
R=$(ls security/semgrep*.yml .semgrep.yml 2>/dev/null | head -1)
if [ -n "$R" ]; then echo "== semgrep ($R)"; V=/tmp/dheeban-sg; [ -x $V/bin/semgrep ] || { python3 -m venv $V && $V/bin/pip -q install semgrep; }
  $V/bin/semgrep --config "$R" --metrics=off . 2>&1 | grep -E "Findings|Ran " ; else echo "== semgrep: لا قواعد محلية (المكتبة العامة تحتاج semgrep.dev)"; fi
