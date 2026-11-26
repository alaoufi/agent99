---
name: dheeban
description: ذيبان — حالة المنظومة العامة وتقرير الاستهلاك والتنسيق بين الجلسات وكودكس. استخدمه عند طلب "ذيبان" أو "/dheeban" أو سؤال عن الاستهلاك أو الأدوات المثبتة أو التواصل مع جلسة أخرى أو كودكس.
---

# ذيبان

نفّذ حسب الطلب، باختصار وبالعربية:

## حالة / فحص
`bash "$(cat ~/.dheeb/source)/install.sh" --check`
ثم `python3 ~/.dheeb/bin/dheeb_report.py` لملخص الاستهلاك والأحداث في هذه الحاوية.

## الاستهلاك عبر الجلسات
الحاويات السحابية مؤقتة، فالسجل المحلي يخص هذه الجلسة فقط. لصورة أوسع: `list_sessions` (mine) وقراءة آخر `result` لكل جلسة عبر `list_events` بـ kinds ["result"] — فقط عند طلب المالك (القراءة نفسها تستهلك).

## التنسيق
- جلسة Claude سحابية: `list_sessions` ← اختر بالعنوان ← `send_message` (priority "later" افتراضيًا كي لا تقاطع).
- كودكس أو جلسة لاحقة: أنشئ Issue في `alaoufi/agent99` بعنوان `[الوجهة] الموضوع` وفق `coordination/PROTOCOL.md`، واقرأ المفتوح الموجّه لمشروعك قبل العمل المشترك.
- الخادم المشترك: `COORDINATION.md` في `alaoufi/server-edge` يتقدّم.

## الذاكرة
حقائق وقرارات دائمة: `memory/MEMORY.md` في `alaoufi/agent99` (اقرأه بـ get_file_contents عند الحاجة فقط). أضف سطرًا مؤرخًا لكل قرار جديد من المالك.

## الوكيل
للمهام الطويلة (جرد شامل، تقرير استهلاك مفصل) فوّض للوكيل `dheeb` (نموذج أخف).

## الأداة أولًا (قاعدة المالك 2026-11-26) — قبل أي عمل حدّد الأداة، ثم نفّذ بها
| نوع المهمة | الأداة المثبتة |
|---|---|
| تصميم واجهة/قالب/صفحة | `frontend-design` + `ui-ux-pro-max` (خطة رموز ← مراجعة ← بناء ← نقد بالصور) |
| نصوص التصميم (تُعمل مع التصميم لا بعده) | `product-marketing` ← `copywriting` ← `copy-editing` ← `cro`، و`marketing-psychology` عند الحاجة، والطباعة من `ui-ux-pro-max` |
| ملصق/صورة تسويقية ثابتة | `canvas-design` |
| خطة تسويق | `marketing-plan` (+ `product-marketing` أولًا) |
| نصوص تسويقية/صفحات | `copywriting` ثم `copy-editing` |
| SEO / ظهور في الذكاء الاصطناعي | `seo-audit` / `programmatic-seo` / `ai-seo` / `schema` |
| فحص سرعة/وصولية/أمان/تحمل | `dheeban-toolbox` |
| ميزة أو إصلاح كود | `superpowers:writing-plans` ثم `superpowers:test-driven-development` + `superpowers:systematic-debugging` للأخطاء |
| مراجعة قبل الدمج | `code-review` + `security-review` |
| PDF / Word / Excel / عروض | `pdf` / `docx` / `xlsx` / `pptx` |
| عمل طويل أو موازٍ | جلسة المشروع الخاصة، أو وكيل بنموذج أخف |
وفي تعليمات أي جلسة أخرى: اذكر الأدوات بالاسم صراحةً.
**الاستهلاك:** إذا نبّه حارس ذيبان أن الجلسة ثقيلة، احفظ التقدم واقترح نقل العمل لجلسة جديدة مع ملف تسليم.
