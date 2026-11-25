#!/usr/bin/env python3
"""تقرير ذيب المحلي: الاستهلاك والأحداث المسجلة في ~/.dheeb."""
import json, os, collections
ST = os.environ.get("DHEEB_STATE", os.path.expanduser("~/.dheeb"))
def rows(name):
    p = os.path.join(ST, name)
    if not os.path.exists(p): return []
    out = []
    for l in open(p, encoding="utf-8"):
        try: out.append(json.loads(l))
        except Exception: pass
    return out
u, e = rows("usage.jsonl"), rows("events.jsonl")
last = {}
for r in u: last[r.get("sid")] = r          # آخر لقطة لكل جلسة
print(f"جلسات مسجلة: {len(last)} | أحداث: {len(e)}")
for r in sorted(last.values(), key=lambda r: -r.get("all", 0))[:10]:
    top = ", ".join(f"{k}:{v}" for k, v in sorted(r.get("by_tool", {}).items(), key=lambda x: -x[1])[:4])
    print(f"- {r.get('sid','?')[:8]} {r.get('cwd','')} | رموز {r.get('all',0):,} (إخراج {r.get('out',0):,}) | أدوات {r.get('tools',0)} [{top}]")
c = collections.Counter(x.get("ev") for x in e)
print("الأحداث:", dict(c))
for x in [x for x in e if x.get("ev") in ("block", "repeat", "usage_warn", "error")][-8:]:
    print(" ", x.get("t"), x.get("ev"), x.get("cmd") or x.get("tool") or x.get("err") or x.get("all", ""))
