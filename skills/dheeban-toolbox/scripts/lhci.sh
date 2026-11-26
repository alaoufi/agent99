#!/usr/bin/env bash
# Lighthouse CI: يجمع عدة صفحات ويتحقق من حدود (lighthouserc.json). جُرّب 2026-11-26 على نسخة محلية. يعمل في GitHub Actions بالأمر نفسه.
# الاستعمال: bash lhci.sh URL1 [URL2 ...]
U=(); for x in "$@"; do U+=(--url="$x"); done
NO_PROXY=127.0.0.1 npx -y @lhci/cli@0.15.1 collect "${U[@]}" --numberOfRuns=1 --chromePath=/opt/pw-browsers/chromium --settings.chromeFlags="--headless --no-sandbox"
[ -f lighthouserc.json ] && npx -y @lhci/cli@0.15.1 assert
