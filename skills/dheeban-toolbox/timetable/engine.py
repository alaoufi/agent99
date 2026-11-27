"""محرك الجداول المدرسية — Google OR-Tools CP-SAT (ortools==9.15.6755).

محرك عام مستقل عن أي مشروع: يقرأ بيانات JSON ويعيد جدولًا أو تشخيصًا عربيًا.
المشروع يحوّل بياناته من قاعدة بياناته الفعلية إلى هذا الشكل (محوّل في المشروع نفسه)،
ثم يحفظ النتيجة في جداوله الموجودة. لا قاعدة بيانات هنا.

الأوامر:
  python engine.py solve    input.json [output.json]   إنشاء/تحسين/إعادة جدولة جزئية
  python engine.py check    input.json schedule.json   فحص تعارضات جدول (يدوي أو قائم)
  python engine.py diagnose input.json                 أسباب تعذر الجدول واقتراحات
"""
from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from ortools.sat.python import cp_model

RIYADH = ZoneInfo("Asia/Riyadh")
DEFAULT_DAYS = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس"]
DEFAULT_WEIGHTS = {"teacher_gap": 3, "class_gap": 5, "same_day_repeat": 4,
                   "day_imbalance": 1, "change_from_previous": 10}


def now_riyadh() -> str:
    return datetime.now(RIYADH).isoformat(timespec="seconds")


# ---------------------------------------------------------------- البيانات
class Data:
    """تطبيع المدخلات وبناء «وحدات الدرس»: (فصول، مادة، عدد حصص)."""

    def __init__(self, raw: dict):
        self.raw = raw
        self.days = raw.get("days") or DEFAULT_DAYS
        self.P = int(raw.get("periods_per_day", 7))
        self.D = len(self.days)
        self.slots = [(d, p) for d in range(self.D) for p in range(self.P)]
        self.teachers = {t["id"]: t for t in raw["teachers"]}
        self.classes = {c["id"]: c for c in raw["classes"]}
        self.subjects = {s["id"]: s for s in raw["subjects"]}
        self.weights = {**DEFAULT_WEIGHTS, **raw.get("weights", {})}
        self.errors: list[dict] = []
        self.units = self._build_units()

    def name(self, kind, i):
        src = {"teacher": self.teachers, "class": self.classes, "subject": self.subjects}[kind]
        return src.get(i, {}).get("name", str(i))

    def can_teach(self, tid, subject, grade) -> bool:
        for c in self.teachers[tid].get("can_teach", []):
            if c["subject"] == subject and (not c.get("grades") or grade in c["grades"]):
                return True
        return False

    def _build_units(self):
        joint_of = {}
        for g in self.raw.get("joint_groups", []):
            grades = {self.classes[c]["grade"] for c in g["classes"]}
            if len(grades) != 1 or not g.get("topic"):
                self.errors.append({"type": "joint_invalid", "group": g["id"],
                                    "message": f"الدمج «{g['id']}» مرفوض: الدمج يشترط نفس المرحلة والمادة وموضوع الدرس."})
                continue
            for c in g["classes"]:
                joint_of[(c, g["subject"])] = g
        units, seen = [], set()
        for r in self.raw["requirements"]:
            key = (r["class"], r["subject"])
            g = joint_of.get(key)
            if g:
                if g["id"] in seen:
                    continue
                seen.add(g["id"])
                cls = list(g["classes"])
                periods = {x["periods"] for x in self.raw["requirements"]
                           if x["subject"] == g["subject"] and x["class"] in cls}
                if len(periods) != 1:
                    self.errors.append({"type": "joint_invalid", "group": g["id"],
                                        "message": f"الدمج «{g['id']}» مرفوض: عدد الحصص المطلوب مختلف بين الفصول."})
                    continue
                units.append({"id": f"J:{g['id']}", "classes": cls, "subject": g["subject"],
                              "n": periods.pop(), "teacher": g.get("teacher"), "topic": g["topic"]})
            else:
                units.append({"id": f"{r['class']}:{r['subject']}", "classes": [r["class"]],
                              "subject": r["subject"], "n": int(r["periods"]), "teacher": r.get("teacher")})
        for u in units:
            grade = self.classes[u["classes"][0]]["grade"]
            if u["teacher"]:
                u["eligible"] = [u["teacher"]]
            else:
                u["eligible"] = [t for t in self.teachers if self.can_teach(t, u["subject"], grade)]
        return units

    def unavailable(self, tid):
        return {tuple(x) for x in self.teachers[tid].get("unavailable", [])}


# ---------------------------------------------------------------- النموذج
class Model:
    def __init__(self, data: Data, with_assumptions=False, previous=None, free_units=None):
        self.d, self.m = data, cp_model.CpModel()
        self.assume: dict[int, dict] = {}  # فهرس الافتراض -> وصف الشرط الإلزامي
        self.with_assumptions = with_assumptions
        self.x, self.y = {}, {}
        self._build(previous or [], set(free_units or []))

    def _guard(self, ct, info):
        """ربط شرط إلزامي بمتغير افتراض حتى يظهر في التشخيص."""
        if self.with_assumptions:
            lit = self.m.NewBoolVar(info["key"])
            ct.OnlyEnforceIf(lit)
            self.assume[lit.Index()] = info | {"lit": lit}

    def _build(self, previous, free_units):
        d, m = self.d, self.m
        busy_t = defaultdict(list)   # (t, d, p) -> vars
        busy_c = defaultdict(list)   # (c, d, p) -> vars
        for u in d.units:
            uid = u["id"]
            for t in u["eligible"]:
                self.y[uid, t] = m.NewBoolVar(f"y_{uid}_{t}")
                for (dd, p) in d.slots:
                    v = m.NewBoolVar(f"x_{uid}_{t}_{dd}_{p}")
                    self.x[uid, t, dd, p] = v
                    m.AddImplication(v, self.y[uid, t])
                    busy_t[t, dd, p].append(v)
                    for c in u["classes"]:
                        busy_c[c, dd, p].append(v)
            ys = [self.y[uid, t] for t in u["eligible"]]
            subj, cls = d.name("subject", u["subject"]), "، ".join(d.name("class", c) for c in u["classes"])
            if not ys:
                continue  # يُكتشف في الفحص المسبق
            self._guard(m.AddExactlyOne(ys), {"key": f"req_{uid}", "kind": "requirement", "unit": uid,
                                              "message": f"تدريس {subj} للفصل {cls}"})
            for t in u["eligible"]:
                tot = sum(self.x[uid, t, dd, p] for (dd, p) in d.slots)
                self._guard(m.Add(tot == u["n"] * self.y[uid, t]),
                            {"key": f"cnt_{uid}_{t}", "kind": "requirement", "unit": uid,
                             "message": f"{u['n']} حصص أسبوعيًا من {subj} للفصل {cls}"})
            mpd = d.subjects[u["subject"]].get("max_per_day", 2)
            for dd in range(d.D):
                m.Add(sum(self.x[uid, t, dd, p] for t in u["eligible"] for p in range(d.P)) <= mpd)

        # منع التعارض: معلم/فصل في حصة واحدة على الأكثر
        for k, vs in busy_t.items():
            if len(vs) > 1:
                m.AddAtMostOne(vs)
        for k, vs in busy_c.items():
            if len(vs) > 1:
                m.AddAtMostOne(vs)

        # أوقات التوفر والنصاب
        for t, info in d.teachers.items():
            un = d.unavailable(t)
            vs = [v for (dd, p) in un for v in busy_t.get((t, dd, p), [])]
            if vs:
                self._guard(m.Add(sum(vs) == 0), {"key": f"avail_{t}", "kind": "availability", "teacher": t,
                                                  "message": f"أوقات عدم توفر المعلم {d.name('teacher', t)}"})
            load = sum(u["n"] * self.y[u["id"], t] for u in d.units if (u["id"], t) in self.y)
            if "max_weekly" in info:
                self._guard(m.Add(load <= info["max_weekly"]), {"key": f"max_{t}", "kind": "load", "teacher": t,
                            "message": f"النصاب الأعلى للمعلم {d.name('teacher', t)} ({info['max_weekly']} حصة)"})
            if info.get("min_weekly"):
                self._guard(m.Add(load >= info["min_weekly"]), {"key": f"min_{t}", "kind": "load", "teacher": t,
                            "message": f"النصاب الأدنى للمعلم {d.name('teacher', t)} ({info['min_weekly']} حصة)"})

        # الحصص المثبتة
        for i, pin in enumerate(d.raw.get("pinned", [])):
            uid = self._unit_of(pin["class"], pin["subject"])
            key = (uid, pin.get("teacher"), pin["day"], pin["period"])
            msg = (f"تثبيت {d.name('subject', pin['subject'])} للفصل {d.name('class', pin['class'])} "
                   f"يوم {d.days[pin['day']]} الحصة {pin['period'] + 1}")
            if key not in self.x:
                d.errors.append({"type": "pin_invalid", "message": msg + ": المعلم غير مؤهل أو البيانات غير صحيحة."})
                continue
            self._guard(m.Add(self.x[key] == 1), {"key": f"pin_{i}", "kind": "pinned", "message": msg})

        # إعادة الجدولة الجزئية: ما ليس في free_units يبقى كما هو (إلزامي)، والباقي يُفضَّل بقاؤه
        change_terms = []
        self.auto_freed = set()
        if free_units:
            # حصة مقفلة صارت تخالف شرطًا إلزاميًا جديدًا (مثل عدم توفر المعلم): تُحرَّر وحدتها ويُبلَّغ بها
            for a in previous:
                if a["teacher"] in d.teachers and (a["day"], a["period"]) in d.unavailable(a["teacher"]):
                    uid = self._unit_of(a["class"], a["subject"])
                    if uid not in free_units:
                        self.auto_freed.add(uid)
            free_units = free_units | self.auto_freed
        for a in previous:
            uid = self._unit_of(a["class"], a["subject"])
            key = (uid, a["teacher"], a["day"], a["period"])
            if key not in self.x:
                continue
            if free_units is not None and uid not in free_units and free_units:
                m.Add(self.x[key] == 1)
            else:
                change_terms.append(1 - self.x[key])

        # التفضيلات المرنة
        W = d.weights
        obj = [W["change_from_previous"] * t for t in change_terms]
        for t in d.teachers:
            for dd in range(d.D):
                b = [self._busy(busy_t.get((t, dd, p), [])) for p in range(d.P)]
                obj += [W["teacher_gap"] * g for g in self._gaps(b, f"t{t}{dd}")]
        for c in d.classes:
            for dd in range(d.D):
                b = [self._busy(busy_c.get((c, dd, p), [])) for p in range(d.P)]
                obj += [W["class_gap"] * g for g in self._gaps(b, f"c{c}{dd}")]
        for u in d.units:
            daily = []
            for dd in range(d.D):
                cnt = m.NewIntVar(0, d.P, "")
                m.Add(cnt == sum(self.x[u["id"], t, dd, p] for t in u["eligible"] for p in range(d.P)))
                rep = m.NewIntVar(0, d.P, "")
                m.Add(rep >= cnt - 1)
                obj.append(W["same_day_repeat"] * rep)
                daily.append(cnt)
            if daily and u["n"] <= d.D:
                hi = m.NewIntVar(0, d.P, "")
                m.AddMaxEquality(hi, daily)
                obj.append(W["day_imbalance"] * hi)
        m.Minimize(sum(obj))

    def _unit_of(self, cls, subj):
        for u in self.d.units:
            if cls in u["classes"] and u["subject"] == subj:
                return u["id"]
        return None

    def _busy(self, vs):
        b = self.m.NewBoolVar("")
        if vs:
            self.m.Add(sum(vs) == b)  # لا تعارض، فالمجموع 0 أو 1
        else:
            self.m.Add(b == 0)
        return b

    def _gaps(self, b, tag):
        """فراغ = حصة فارغة بين حصتين مشغولتين في اليوم نفسه."""
        m, P, gaps = self.m, len(b), []
        before = [m.NewBoolVar("") for _ in range(P)]
        after = [m.NewBoolVar("") for _ in range(P)]
        for p in range(P):
            m.AddMaxEquality(before[p], b[:p] or [m.NewConstant(0)])
            m.AddMaxEquality(after[p], b[p + 1:] or [m.NewConstant(0)])
            g = m.NewBoolVar("")
            m.Add(g >= before[p] + after[p] - 1 - b[p])
            gaps.append(g)
        return gaps


# ---------------------------------------------------------------- الفحص المسبق
def precheck(d: Data) -> list[dict]:
    """فحوص سريعة بلا محرك تحدد السبب المباشر وتقترح حلًا."""
    out = list(d.errors)
    slots = d.D * d.P
    class_load = defaultdict(int)
    teacher_need = defaultdict(int)
    for u in d.units:
        for c in u["classes"]:
            class_load[c] += u["n"]
        subj, cls = d.name("subject", u["subject"]), "، ".join(d.name("class", c) for c in u["classes"])
        if not u["eligible"]:
            out.append({"type": "no_teacher", "unit": u["id"],
                        "message": f"لا يوجد معلم مؤهل لتدريس {subj} للفصل {cls}.",
                        "suggestions": ["أضف التخصص/الصف لأحد المعلمين", "أو أسند المادة لمعلم محدد"]})
        elif len(u["eligible"]) == 1:
            teacher_need[u["eligible"][0]] += u["n"]
        mpd = d.subjects[u["subject"]].get("max_per_day", 2)
        if u["n"] > mpd * d.D:
            out.append({"type": "too_many_periods", "unit": u["id"],
                        "message": f"{subj} للفصل {cls}: {u['n']} حصص لا تتسع مع حد {mpd} في اليوم × {d.D} أيام.",
                        "suggestions": [f"ارفع max_per_day للمادة إلى {-(-u['n'] // d.D)}", "أو قلّل الحصص المطلوبة"]})
    for c, n in class_load.items():
        if n > slots:
            out.append({"type": "class_overload", "class": c,
                        "message": f"الفصل {d.name('class', c)} يحتاج {n} حصة والأسبوع فيه {slots} فقط.",
                        "suggestions": ["قلّل حصص بعض المواد", "أو زد عدد الحصص اليومية"]})
    for t, n in teacher_need.items():
        info = d.teachers[t]
        free = slots - len(d.unavailable(t))
        nm = d.name("teacher", t)
        if n > free:
            out.append({"type": "teacher_availability", "teacher": t,
                        "message": f"المعلم {nm} وحده المؤهل لـ {n} حصة لكنه متاح {free} حصة فقط.",
                        "suggestions": ["وسّع أوقات توفره", "أو أهّل معلمًا آخر لبعض مواده"]})
        if n > info.get("max_weekly", 10**9):
            out.append({"type": "teacher_load", "teacher": t,
                        "message": f"المعلم {nm} وحده المؤهل لـ {n} حصة ونصابه {info['max_weekly']}.",
                        "suggestions": ["ارفع نصابه بموافقة الإدارة", "أو أهّل معلمًا آخر", "أو استخدم الدمج المسموح"]})
    return out


# ---------------------------------------------------------------- الأوامر
def _params(time_limit, workers):
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = float(time_limit)
    s.parameters.num_workers = workers
    s.parameters.random_seed = 1
    return s


def solve(raw: dict, time_limit=30, workers=8) -> dict:
    t0 = time.perf_counter()
    d = Data(raw)
    pre = precheck(d)
    if pre:
        return {"status": "INFEASIBLE", "generated_at": now_riyadh(), "diagnosis": pre,
                "message": "تعذّر إنشاء الجدول بسبب شروط إلزامية متعارضة. لم يُتجاوز أي شرط."}
    pr = raw.get("partial", {})
    mdl = Model(d, previous=raw.get("previous", []), free_units=pr.get("free_units"))
    s = _params(time_limit, workers)
    first = []

    class _First(cp_model.CpSolverSolutionCallback):
        def on_solution_callback(self):
            if not first:
                first.append(round(time.perf_counter() - t0, 3))

    st = s.Solve(mdl.m, _First())
    name = s.StatusName(st)
    res = {"status": name, "generated_at": now_riyadh(), "seconds": round(time.perf_counter() - t0, 3),
           "first_solution_seconds": first[0] if first else None, "engine": "ortools-cp-sat 9.15.6755",
           "auto_freed_units": sorted(mdl.auto_freed)}
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        res["diagnosis"] = diagnose(raw, time_limit=time_limit)["diagnosis"]
        res["message"] = "تعذّر إنشاء الجدول. راجع التشخيص؛ لم يُتجاوز أي شرط إلزامي."
        return res
    sched = []
    for (uid, t, dd, p), v in mdl.x.items():
        if s.Value(v):
            u = next(u for u in d.units if u["id"] == uid)
            for c in u["classes"]:
                sched.append({"class": c, "subject": u["subject"], "teacher": t, "day": dd, "period": p,
                              "joint": uid if uid.startswith("J:") else None})
    sched.sort(key=lambda a: (a["class"], a["day"], a["period"]))
    res.update({"objective": s.ObjectiveValue(), "schedule": sched, "conflicts": check(raw, sched),
                "stats": stats(d, sched)})
    return res


def diagnose(raw: dict, time_limit=30) -> dict:
    d = Data(raw)
    pre = precheck(d)
    if pre:
        return {"status": "INFEASIBLE", "diagnosis": pre}
    mdl = Model(d, with_assumptions=True)
    mdl.m.ClearObjective()
    mdl.m.AddAssumptions([i["lit"] for i in mdl.assume.values()])
    s = _params(time_limit, 1)  # استخراج النواة يحتاج عاملًا واحدًا
    st = s.Solve(mdl.m)
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return {"status": "FEASIBLE", "diagnosis": []}
    core = [mdl.assume[i] for i in s.SufficientAssumptionsForInfeasibility() if i in mdl.assume]
    items = [{"type": "conflict_core", "kind": c["kind"], "message": c["message"],
              **{k: c[k] for k in ("teacher", "unit") if k in c}} for c in core]
    sugg = {"availability": "وسّع أوقات توفر المعلم", "load": "راجع نصاب المعلم",
            "pinned": "ألغِ تثبيت هذه الحصة أو انقلها", "requirement": "قلّل الحصص أو أهّل معلمًا إضافيًا"}
    for it in items:
        it["suggestions"] = [sugg[it["kind"]]]
    head = {"type": "summary", "message": f"هذه الشروط الإلزامية ({len(items)}) لا يمكن تحقيقها معًا؛ تخفيف أي واحد منها يفتح الحل."}
    return {"status": "INFEASIBLE", "diagnosis": [head] + items}


def check(raw: dict, schedule: list[dict]) -> list[dict]:
    """فحص فوري لجدول (يدوي أو ناتج) بلا محرك: سريع للتعديل اليدوي."""
    d = Data(raw)
    out, tslot, cslot = [], defaultdict(list), defaultdict(list)
    joint_ok = {u["id"]: set(u["classes"]) for u in d.units if u["id"].startswith("J:")}
    for a in schedule:
        key = (a["day"], a["period"])
        tslot[a["teacher"], key].append(a)
        cslot[a["class"], key].append(a)
        tn, cn, sn = d.name("teacher", a["teacher"]), d.name("class", a["class"]), d.name("subject", a["subject"])
        when = f"{d.days[a['day']]} الحصة {a['period'] + 1}"
        if a["teacher"] in d.teachers and key in d.unavailable(a["teacher"]):
            out.append({"type": "unavailable", "message": f"{tn} غير متاح {when}."})
        grade = d.classes[a["class"]]["grade"]
        if a["teacher"] in d.teachers and not d.can_teach(a["teacher"], a["subject"], grade):
            fixed = any(u.get("teacher") == a["teacher"] and a["class"] in u["classes"] for u in d.units)
            if not fixed:
                out.append({"type": "not_qualified", "message": f"{tn} غير مصرح له بتدريس {sn} للصف {grade}."})
    for (t, key), lst in tslot.items():
        groups = {a.get("joint") for a in lst}
        if len(lst) > 1 and not (len(groups) == 1 and None not in groups
                                 and {a["class"] for a in lst} <= joint_ok.get(groups.pop(), set())):
            out.append({"type": "teacher_clash", "message": f"تعارض: {d.name('teacher', t)} في {len(lst)} فصول "
                        f"{d.days[key[0]]} الحصة {key[1] + 1}."})
    for (c, key), lst in cslot.items():
        if len(lst) > 1:
            out.append({"type": "class_clash", "message": f"تعارض: الفصل {d.name('class', c)} لديه {len(lst)} حصص "
                        f"{d.days[key[0]]} الحصة {key[1] + 1}."})
    need = {(c, r["subject"]): r["periods"] for r in raw["requirements"] for c in [r["class"]]}
    have = defaultdict(int)
    for a in schedule:
        have[a["class"], a["subject"]] += 1
    for k, n in need.items():
        if have[k] != n:
            out.append({"type": "count", "message": f"الفصل {d.name('class', k[0])}: {d.name('subject', k[1])} "
                        f"{have[k]} من {n} حصص مطلوبة."})
    load = defaultdict(set)
    for a in schedule:
        load[a["teacher"]].add((a["day"], a["period"]))
    for t, s in load.items():
        mx = d.teachers.get(t, {}).get("max_weekly")
        if mx is not None and len(s) > mx:
            out.append({"type": "load", "message": f"{d.name('teacher', t)}: {len(s)} حصة تتجاوز النصاب {mx}."})
    return out


def stats(d: Data, sched) -> dict:
    tgap = cgap = 0
    by_t, by_c = defaultdict(set), defaultdict(set)
    for a in sched:
        by_t[a["teacher"], a["day"]].add(a["period"])
        by_c[a["class"], a["day"]].add(a["period"])
    for s in by_t.values():
        tgap += max(s) - min(s) + 1 - len(s)
    for s in by_c.values():
        cgap += max(s) - min(s) + 1 - len(s)
    return {"lessons": len(sched), "teacher_gaps": tgap, "class_gaps": cgap}


def views(raw: dict, sched: list[dict]) -> dict:
    """جداول المعلمين والفصول والطلاب (الطالب يتبع فصله)."""
    d = Data(raw)
    grid = lambda: [[None] * d.P for _ in range(d.D)]
    t, c = defaultdict(grid), defaultdict(grid)
    for a in sched:
        t[a["teacher"]][a["day"]][a["period"]] = f"{d.name('subject', a['subject'])} — {d.name('class', a['class'])}"
        c[a["class"]][a["day"]][a["period"]] = f"{d.name('subject', a['subject'])} — {d.name('teacher', a['teacher'])}"
    students = {s["id"]: c[s["class"]] for s in raw.get("students", [])}
    return {"teachers": dict(t), "classes": dict(c), "students": students}


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    cmd, raw = argv[1], json.load(open(argv[2], encoding="utf-8"))
    if cmd == "solve":
        res = solve(raw, time_limit=raw.get("time_limit", 30))
    elif cmd == "check":
        res = {"conflicts": check(raw, json.load(open(argv[3], encoding="utf-8")))}
    elif cmd == "diagnose":
        res = diagnose(raw)
    else:
        print(__doc__)
        return 2
    out = json.dumps(res, ensure_ascii=False, indent=1)
    if cmd == "solve" and len(argv) > 3:
        open(argv[3], "w", encoding="utf-8").write(out)
        print(json.dumps({k: res.get(k) for k in ("status", "seconds", "stats", "message")}, ensure_ascii=False))
    else:
        print(out)
    return 0 if res.get("status", "OK") in ("OPTIMAL", "FEASIBLE", "OK") or cmd == "check" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
