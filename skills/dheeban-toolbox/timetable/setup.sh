#!/usr/bin/env bash
# تثبيت OR-Tools بإصدار مثبت في بيئة معزولة (مرة لكل حاوية؛ لا يعيد التثبيت إن وُجد)
set -euo pipefail
V="${ORTOOLS_VENV:-$HOME/.dheeb/venv-ortools}"
if "$V/bin/python" -c "import ortools,sys; sys.exit(ortools.__version__!='9.15.6755')" 2>/dev/null; then
  echo "OR-Tools 9.15.6755 مثبت في $V"; exit 0; fi
python3 -m venv "$V" && "$V/bin/pip" install -q "ortools==9.15.6755"
echo "ثُبّت OR-Tools 9.15.6755 في $V — المحرك: $V/bin/python $(dirname "$0")/engine.py"
