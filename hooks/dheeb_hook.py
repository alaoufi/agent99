#!/usr/bin/env python3
"""ذيبان (DHEEB) — خطّاف عام واحد لكل الجلسات: سياق البدء، حارس الأدوات، مراقبة الاستهلاك.

يُستدعى من ~/.claude/settings.json بالحدث في أول وسيط:
  dheeb_hook.py session|pre|post|stop
لا يُسقط الجلسة أبدًا: أي خطأ داخلي يُبلع ويُسجَّل، ويخرج بـ 0.
"""
import json, os, re, sys, time, hashlib

HOME = os.path.expanduser("~")
STATE = os.environ.get("DHEEB_STATE", os.path.join(HOME, ".dheeb"))
POLICY_FILE = os.path.join(STATE, "policy.json")
DEFAULT_POLICY = {
    "repeat_warn": 3,          # تكرار الأمر نفسه حرفيًا
    "check_every": 25,         # كل كم أداة نقرأ الاستهلاك من السجل
    "warn_tokens": 3_000_000,  # إجمالي الرموز (مع الكاش) لتنبيه أول
    "warn_output": 60_000,     # رموز الإخراج لتنبيه أول
    "big_file_lines": 1500,    # ملف أكبر من هذا يُقرأ بأجزاء
}
# أوامر هدر معروفة في بيئات Claude السحابية: (نمط، سبب)
BLOCK = [
    (r"\bplaywright\s+install\b", "Playwright والمتصفح مثبتان مسبقًا؛ إعادة التثبيت هدر وتكسر المسار. استخدم require('playwright') مباشرة."),
    (r"npm\s+(i|install)\s+(-g|--global)\s+@anthropic-ai/claude-code", "Claude Code مثبت مسبقًا؛ لا تعِد تثبيته."),
    (r"\bapt(-get)?\s+install\b.*\b(chromium|google-chrome)\b", "Chromium مثبت في /opt/pw-browsers/chromium."),
]
ADVISE = [
    (r"(^|[;&|]\s*)(grep|egrep)\s+-[a-zA-Z]*r", "للبحث الواسع استخدم أداة Grep (أسرع وأقل إخراجًا) أو استثنِ node_modules و.git."),
    (r"(^|[;&|]\s*)find\s+/\s", "find من الجذر مكلف؛ حدّد مجلدًا أو استخدم Glob."),
]


def load(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    os.replace(tmp, path)


def log(kind, **kw):
    os.makedirs(STATE, exist_ok=True)
    kw.update(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), ev=kind)
    with open(os.path.join(STATE, "events.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(kw, ensure_ascii=False) + "\n")


def out(event, context=None, decision=None, reason=None):
    spec = {"hookEventName": event}
    if context:
        spec["additionalContext"] = context
    if decision:
        spec["permissionDecision"] = decision
        spec["permissionDecisionReason"] = reason or ""
    print(json.dumps({"hookSpecificOutput": spec}, ensure_ascii=False))


def usage(transcript):
    """يجمع الاستهلاك من سجل الجلسة مع إزالة تكرار الرسالة الواحدة."""
    seen, tot = set(), {"in": 0, "out": 0, "cache_r": 0, "cache_w": 0, "msgs": 0}
    try:
        with open(transcript, encoding="utf-8") as f:
            for line in f:
                if '"usage"' not in line:
                    continue
                try:
                    m = json.loads(line).get("message") or {}
                except Exception:
                    continue
                u, mid = m.get("usage"), m.get("id")
                if not u or mid in seen:
                    continue
                seen.add(mid)
                tot["msgs"] += 1
                tot["in"] += u.get("input_tokens", 0) or 0
                tot["out"] += u.get("output_tokens", 0) or 0
                tot["cache_r"] += u.get("cache_read_input_tokens", 0) or 0
                tot["cache_w"] += u.get("cache_creation_input_tokens", 0) or 0
    except Exception:
        pass
    tot["all"] = tot["in"] + tot["out"] + tot["cache_r"] + tot["cache_w"]
    return tot


def file_lines(path):
    try:
        if os.path.getsize(path) > 50_000_000:
            return 10**9
        with open(path, "rb") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def on_session(d, pol):
    sid = d.get("session_id", "?")
    log("session", sid=sid, cwd=d.get("cwd"), source=d.get("source"))
    mem = os.path.join(STATE, "MEMORY.md")
    ctx = [
        "ذيبان (DHEEB) مفعّل في هذه الجلسة على مستوى المستخدم:",
        "- اللغة: اكتب للمالك بالعربية دائمًا (الردود والأسئلة ورسائل التقدم والملخصات)، إلا الكود والأوامر وما تشترطه الأدوات.",
        "- الاقتصاد أولًا: اقرأ الجزء اللازم فقط (Grep/Glob/Read بحدود)، لا تكرر الأمر نفسه، لا تُعِد تثبيت المثبَّت، ووكيل فرعي فقط للعمل الموازي الحقيقي.",
        "- الحارس قد يمنع أوامر هدر معروفة ويذكر السبب؛ اتبع البديل المقترح بدل الالتفاف عليه.",
        "- لا تتدخل في جلسات أو فروع أو موارد مشاريع أخرى؛ قواعد CLAUDE.md للمشروع تتقدّم على ذيبان.",
        "- ذاكرة ذيبان وأدواته في المستودع الخاص alaoufi/agent99؛ لا تفتحه إلا إذا كان الطلب يخص ذيبان أو التنسيق بين المشاريع/الجلسات/كودكس.",
        "- التنسيق: Issues في alaoufi/agent99 بعنوان يبدأ [للمشروع] أو [codex] أو [all]، وsend_message بين جلسات Claude السحابية. التفاصيل: مهارة /dheeban.",
    ]
    if os.path.exists(mem):
        ctx.append(f"- ملخص الذاكرة المحلي: {mem}")
    out("SessionStart", "\n".join(ctx))


def on_pre(d, pol):
    tool, ti = d.get("tool_name", ""), d.get("tool_input") or {}
    if tool == "Bash":
        cmd = ti.get("command", "")
        for pat, why in BLOCK:
            if re.search(pat, cmd):
                log("block", sid=d.get("session_id"), cmd=cmd[:200])
                return out("PreToolUse", decision="deny", reason="ذيبان: " + why)
        m = re.match(r"\s*cat\s+([^\s|;&<>]+)\s*$", cmd)
        if m and file_lines(os.path.join(d.get("cwd") or "", os.path.expanduser(m.group(1)))) > pol["big_file_lines"]:
            log("block", sid=d.get("session_id"), cmd=cmd[:200])
            return out("PreToolUse", decision="deny",
                       reason=f"ذيبان: الملف أكبر من {pol['big_file_lines']} سطر؛ اقرأ الجزء اللازم (sed -n 'A,Bp' أو Read مع offset/limit أو Grep).")
        for pat, why in ADVISE:
            if re.search(pat, cmd):
                return out("PreToolUse", context="ذيبان: " + why)
    elif tool == "Read" and not ti.get("limit"):
        if file_lines(ti.get("file_path", "")) > pol["big_file_lines"]:
            return out("PreToolUse", context="ذيبان: ملف كبير؛ إن كنت تحتاج جزءًا فاقرأه بـ offset/limit أو ابحث بـ Grep.")


def on_post(d, pol):
    sid = d.get("session_id", "x")
    sp = os.path.join(STATE, "sessions", re.sub(r"[^\w-]", "_", sid) + ".json")
    st = load(sp, {"n": 0, "tools": {}, "cmds": {}, "warned": 0})
    tool, ti = d.get("tool_name", "?"), d.get("tool_input") or {}
    st["n"] += 1
    st["tools"][tool] = st["tools"].get(tool, 0) + 1
    notes = []
    if tool in ("Bash", "Read", "Grep", "Glob", "WebFetch"):
        key = hashlib.sha1(json.dumps([tool, ti], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
        c = st["cmds"][key] = st["cmds"].get(key, 0) + 1
        if c == pol["repeat_warn"]:
            notes.append(f"ذيبان: نفّذت الاستدعاء نفسه ({tool}) {c} مرات بلا تغيير؛ غيّر المقاربة أو توقف واسأل بدل التكرار.")
            log("repeat", sid=sid, tool=tool)
    if st["n"] % pol["check_every"] == 0 and d.get("transcript_path"):
        u = usage(d["transcript_path"])
        level = int(u["all"] >= pol["warn_tokens"] * 2 ** st["warned"] or u["out"] >= pol["warn_output"] * 2 ** st["warned"])
        if level:
            st["warned"] += 1
            notes.append(f"ذيبان: استهلاك الجلسة مرتفع (إجمالي {u['all']:,} رمز، إخراج {u['out']:,}، {st['n']} أداة). "
                         "اختصر: لا تعِد قراءة ما قرأته، اجمع الاستدعاءات المستقلة، وإن طال العمل فاحفظ التقدم واقترح إكماله في جلسة جديدة.")
            log("usage_warn", sid=sid, **u)
    save(sp, st)
    if notes:
        out("PostToolUse", "\n".join(notes))


def on_stop(d, pol):
    sid = d.get("session_id", "x")
    st = load(os.path.join(STATE, "sessions", re.sub(r"[^\w-]", "_", sid) + ".json"), {})
    u = usage(d.get("transcript_path", "")) if d.get("transcript_path") else {}
    rec = {"sid": sid, "cwd": d.get("cwd"), "tools": st.get("n", 0), "by_tool": st.get("tools", {}), **u}
    os.makedirs(STATE, exist_ok=True)
    with open(os.path.join(STATE, "usage.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(rec, t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())), ensure_ascii=False) + "\n")


def main():
    ev = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        d = json.load(sys.stdin)
    except Exception:
        d = {}
    pol = dict(DEFAULT_POLICY, **load(POLICY_FILE, {}))
    try:
        {"session": on_session, "pre": on_pre, "post": on_post, "stop": on_stop}.get(ev, lambda *_: None)(d, pol)
    except Exception as e:  # لا نكسر جلسة المستخدم أبدًا
        try:
            log("error", where=ev, err=repr(e)[:300])
        except Exception:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
