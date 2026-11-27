"""اختبارات محرك الجداول: طبيعية ومعقدة واستثنائية + قياس السرعة.
التشغيل: ~/.dheeb/venv-ortools/bin/python -m unittest -v test_engine (من مجلد timetable)
"""
import copy
import os
import resource
import time
import unittest

import engine
from sample import school

FAST = {"time_limit": 20}


def run(raw):
    return engine.solve(raw, time_limit=raw.get("time_limit", 20))


class Normal(unittest.TestCase):
    def test_small_school_no_conflicts(self):
        raw = school(2, 2) | FAST
        r = run(raw)
        self.assertIn(r["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(r["conflicts"], [])
        self.assertEqual(r["stats"]["lessons"], sum(q["periods"] for q in raw["requirements"]))

    def test_availability_and_qualification_respected(self):
        raw = school(2, 2) | FAST
        r = run(raw)
        d = engine.Data(raw)
        for a in r["schedule"]:
            self.assertNotIn((a["day"], a["period"]), d.unavailable(a["teacher"]))
            self.assertTrue(d.can_teach(a["teacher"], a["subject"], d.classes[a["class"]]["grade"]))

    def test_views_teacher_class_student(self):
        raw = school(1, 2) | FAST
        r = run(raw)
        v = engine.views(raw, r["schedule"])
        self.assertTrue(v["teachers"] and v["classes"] and v["students"])
        sid = raw["students"][0]
        self.assertEqual(v["students"][sid["id"]], v["classes"][sid["class"]])


class Complex(unittest.TestCase):
    def test_joint_teaching_same_grade_subject_topic(self):
        raw = school(1, 2) | FAST
        raw["joint_groups"] = [{"id": "pe1", "classes": ["g1a", "g1b"], "subject": "pe", "topic": "كرة القدم"}]
        r = run(raw)
        self.assertIn(r["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(r["conflicts"], [])
        pe = [a for a in r["schedule"] if a["subject"] == "pe"]
        slots_a = {(a["day"], a["period"], a["teacher"]) for a in pe if a["class"] == "g1a"}
        slots_b = {(a["day"], a["period"], a["teacher"]) for a in pe if a["class"] == "g1b"}
        self.assertEqual(slots_a, slots_b)  # الفصلان معًا وبالمعلم نفسه

    def test_joint_rejected_for_different_grades(self):
        raw = school(2, 1) | FAST
        raw["joint_groups"] = [{"id": "bad", "classes": ["g1a", "g2a"], "subject": "pe", "topic": "جري"}]
        r = run(raw)
        self.assertEqual(r["status"], "INFEASIBLE")
        self.assertTrue(any(x["type"] == "joint_invalid" for x in r["diagnosis"]))

    def test_pinned_lessons_kept(self):
        raw = school(2, 2) | FAST
        t = next(t["id"] for t in raw["teachers"] if t["can_teach"][0]["subject"] == "mat")
        raw["pinned"] = [{"class": "g1a", "subject": "mat", "teacher": t, "day": 0, "period": 0}]
        r = run(raw)
        self.assertIn({"class": "g1a", "subject": "mat", "teacher": t, "day": 0, "period": 0, "joint": None},
                      r["schedule"])

    def test_partial_reschedule_keeps_rest(self):
        raw = school(2, 2) | FAST
        first = run(raw)["schedule"]
        raw2 = copy.deepcopy(raw)
        raw2["previous"] = first
        raw2["partial"] = {"free_units": ["g1a:mat"]}
        # المعلم صار غير متاح أول حصتين يوم الأحد
        for a in first:
            if a["class"] == "g1a" and a["subject"] == "mat":
                tid = a["teacher"]
        raw2["teachers"] = [t | ({"unavailable": t.get("unavailable", []) + [[0, 0], [0, 1]]} if t["id"] == tid else {})
                            for t in raw2["teachers"]]
        r = run(raw2)
        self.assertIn(r["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(r["conflicts"], [])
        self.assertFalse(any(a["teacher"] == tid and (a["day"], a["period"]) in {(0, 0), (0, 1)} for a in r["schedule"]))
        keep = lambda s: {(a["class"], a["subject"], a["day"], a["period"]) for a in s if a["class"] != "g1a" or a["subject"] != "mat"}
        # كل ما سوى الوحدة المحررة وما يشترك معها في معلمها يبقى كما هو
        self.assertTrue(keep(first) <= keep(r["schedule"]) | {(a["class"], a["subject"], a["day"], a["period"]) for a in first if a["teacher"] == tid})


class Exceptional(unittest.TestCase):
    def test_overloaded_sole_teacher_named(self):
        raw = school(2, 2) | FAST
        raw["teachers"] = [t for t in raw["teachers"] if t["can_teach"][0]["subject"] != "ara"]
        raw["teachers"].append({"id": "tz", "name": "أ. سارة", "max_weekly": 10,
                                "can_teach": [{"subject": "ara", "grades": [1, 2]}]})
        r = run(raw)
        self.assertEqual(r["status"], "INFEASIBLE")
        self.assertTrue(any("أ. سارة" in x["message"] and x["type"] == "teacher_load" for x in r["diagnosis"]))
        self.assertTrue(all(x.get("suggestions") for x in r["diagnosis"] if x["type"] == "teacher_load"))

    def test_no_qualified_teacher(self):
        raw = school(1, 1) | FAST
        raw["teachers"] = [t for t in raw["teachers"] if t["can_teach"][0]["subject"] != "sci"]
        r = run(raw)
        self.assertTrue(any(x["type"] == "no_teacher" for x in r["diagnosis"]))

    def test_core_pinned_vs_availability(self):
        raw = school(1, 1) | FAST
        t = next(t for t in raw["teachers"] if t["can_teach"][0]["subject"] == "mat")
        t["unavailable"] = [[0, 0]]
        raw["teachers"] = [x for x in raw["teachers"] if x["can_teach"][0]["subject"] != "mat"] + [t]
        raw["pinned"] = [{"class": "g1a", "subject": "mat", "teacher": t["id"], "day": 0, "period": 0}]
        r = engine.diagnose(raw)
        self.assertEqual(r["status"], "INFEASIBLE")
        kinds = {x.get("kind") for x in r["diagnosis"]}
        self.assertTrue({"pinned", "availability"} <= kinds, r["diagnosis"])

    def test_manual_edit_clash_detected(self):
        raw = school(1, 2) | FAST
        s = run(raw)["schedule"]
        a, b = s[0], next(x for x in s if x["class"] != s[0]["class"])
        b = b | {"teacher": a["teacher"], "day": a["day"], "period": a["period"], "subject": a["subject"]}
        bad = [x for x in s if x is not b] + [b]
        types = {c["type"] for c in engine.check(raw, bad)}
        self.assertIn("teacher_clash", types)

    def test_class_overload(self):
        raw = school(1, 1, periods_per_day=5) | FAST
        raw["requirements"].append({"class": "g1a", "subject": "mat", "periods": 30})
        r = run(raw)
        self.assertTrue(any(x["type"] in ("class_overload", "too_many_periods") for x in r["diagnosis"]))


class Benchmark(unittest.TestCase):
    def test_speed_medium_school(self):
        g, s = int(os.environ.get("TT_GRADES", 6)), int(os.environ.get("TT_SECTIONS", 3))
        raw = school(g, s) | {"time_limit": 60}
        t0 = time.perf_counter()
        r = run(raw)
        dt = time.perf_counter() - t0
        rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
        print(f"\n[قياس] {g*s} فصول، {len(raw['teachers'])} معلم، {r['stats']['lessons']} حصة: "
              f"{r['status']} في {dt:.1f} ث (أول حل صالح {r['first_solution_seconds']} ث)، ذاكرة قصوى {rss} MB، فراغات المعلمين {r['stats']['teacher_gaps']}، "
              f"فراغات الفصول {r['stats']['class_gaps']}")
        self.assertIn(r["status"], ("OPTIMAL", "FEASIBLE"))
        self.assertEqual(r["conflicts"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
