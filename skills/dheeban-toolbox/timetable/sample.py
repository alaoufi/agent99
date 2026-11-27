"""مولّد بيانات مدرسة تجريبية بحجم قابل للتعديل (للاختبار وقياس السرعة)."""
import json
import sys

SUBJECTS = [("qur", "القرآن الكريم", 4), ("ara", "لغتي", 5), ("mat", "الرياضيات", 5),
            ("sci", "العلوم", 4), ("eng", "الإنجليزي", 3), ("soc", "الاجتماعيات", 2),
            ("dig", "المهارات الرقمية", 2), ("art", "التربية الفنية", 2), ("pe", "التربية البدنية", 2)]


def school(grades=3, sections=2, periods_per_day=7, seed_unavail=True):
    classes, reqs, teachers = [], [], []
    for g in range(1, grades + 1):
        for s in range(sections):
            cid = f"g{g}{'abcdef'[s]}"
            classes.append({"id": cid, "name": f"{g}/{'أبجدهو'[s]}", "grade": g})
            for sid, _, n in SUBJECTS:
                reqs.append({"class": cid, "subject": sid, "periods": n})
    # معلمان لكل مادة تقريبًا حسب العبء، كل منهم مصرح له بكل الصفوف
    tid = 0
    for sid, name, n in SUBJECTS:
        need = n * grades * sections
        count = max(1, -(-need // 22))
        for k in range(count):
            tid += 1
            t = {"id": f"t{tid}", "name": f"معلم {name} {k + 1}", "max_weekly": 24,
                 "can_teach": [{"subject": sid, "grades": list(range(1, grades + 1))}]}
            if seed_unavail and tid % 4 == 0:
                t["unavailable"] = [[tid % 5, p] for p in range(periods_per_day - 2, periods_per_day)]
            teachers.append(t)
    return {"periods_per_day": periods_per_day, "classes": classes, "teachers": teachers,
            "subjects": [{"id": s, "name": n, "max_per_day": 2} for s, n, _ in SUBJECTS],
            "requirements": reqs,
            "students": [{"id": f"s_{c['id']}_1", "class": c["id"]} for c in classes]}


if __name__ == "__main__":
    g, s = (int(a) for a in sys.argv[1:3]) if len(sys.argv) > 2 else (3, 2)
    print(json.dumps(school(g, s), ensure_ascii=False, indent=1))
