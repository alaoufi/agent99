# تسليم ذيبان — 2026-11-26 مساءً (من session_01NXwKTYM2bbtod9iMQ7LxLJ)

اقرأ هذا ثم memory/MEMORY.md وskills/dheeban/SKILL.md. اكتب للمالك بالعربية وباختصار، وابدأ كل بند باسم المشروع.

## قرار المالك الأهم الآن
- ذيبان لم يعد ينسّق عمل المشاريع. المالك يتعامل مع كل جلسة مشروع رسمية مباشرة.
- مهمة ذيبان: البحث عن الأدوات والمهارات والإضافات وتثبيتها وتوجيه الجلسات لاستخدامها، وفحص المواقع (قراءة فقط). أي تعديل على مشروع يُكتب برومبت يلصقه المالك بنفسه في جلسة المشروع الرسمية.
- لا تفتح جلسات جديدة إلا للضرورة، ووسمها «ذيبان»، وأرشفها بعد انتهائها.

## حالة اليوم
- الأدوات: صندوق dheeban-toolbox فيه الآن Unlighthouse وLHCI وknip وsize-limit وfonttools وmobsfscan وفحص الترويسات والأحجام والروابط (commit e465eed). المرحلة 2 مؤجلة: lychee وGitleaks وhadolint وk6 (منع المصنِّف تنزيل الثنائيات).
- 2026-11-27: المرحلة 2 (Gitleaks وlychee وhadolint وk6) مجرَّبة في GitHub Actions بموافقة المالك؛ انظر dheeban-toolbox.
- إضافات اقتُرحت للتفعيل في حساب claude.ai ولم يتأكد تفعيلها (ListPlugins أعاد فارغًا): frontend-design، Design، Superpowers، Claude Security.
- فحص المواقع الثلاثة: الفرع reports/sites-2026-11-26 (report.md وprompt.md لكل من jdtna.sa وaykdmh.com وtrbhh.sa). أُرسلت البرومبتات للمالك.
- مواقع المالك محجوبة من بيئة Default؛ الفحص الحي يعمل من بيئة aykdmh.
- سكربت بيئة Default قديم؛ تحديثه يحتاج المالك على كمبيوتر.

## 2026-11-27 (session_01NXwKTaXaeUXmKLywdMnaj8)
- المرحلة 2 من الصندوق تعمل في Actions (run 3 ناجح). نقطة تراجع: backup/2026-11-27-toolbox-phase2.
- محرك جداول مدرسية OR-Tools CP-SAT 9.15.6755 في skills/dheeban-toolbox/timetable (13 اختبارًا ناجحًا). نقطة تراجع: backup/2026-11-27-before-ortools.
- **ينتظر المالك:** اسم مشروع النظام الإداري المدرسي، ثم يلصق timetable/PROJECT_PROMPT.md في جلسته الرسمية. وحذف الفرع المدموج dheeban/toolbox-phase2 (بإذنه). وبرومبتا jdtna.sa وaykdmh.com ما زالا عنده.

## 2026-11-27 مساءً — «خطوة» (alaoufi/khatwa-learning)
- نُقل من كودكس إلى Claude. فرع النشر deploy/school-online-20261126 عند 4a79d5e (Render srv-dc46dfbl550s738b2h5g، يدوي النشر؛ موصل Render في جلسة ذيبان unauthorized). قاعدة Neon wild-river-14634954.
- منجز: مدخل موحد للأدوار الأربعة، تصميم احترافي v2، قوائم Tabulator (CSP self بموافقة المالك)، تبويبات، إدارة داخل APK، جدولة آلية OR-Tools (scheduling/)، دخول تجريبي (DEMO_LOGIN=1 في Render).
- APK: سير العمل android-apk.yml يدوي (يُشغّل من ذيبان بـ actions_run_trigger على فرع النشر) وينشر على فرع apk-builds؛ ذيبان يجلبه بـ git ويرسله بـ SendUserFile. التوقيع debug متغير ⇒ حذف القديم قبل التثبيت (اقتُرح مفتاح ثابت كسرّ).
- الجلسة الحالية للمشروع: session_01NXwKTZUAjPcacon5eBLdYA (تعميم الأدوات). ذيبان يدمج في فرع النشر بعد موافقة المالك على الصور وبعد نجاح الاختبارات (لا دفع عند أي فشل).
- موافقات المالك المنقولة عبر ذيبان تُرفض في القرارات الأمنية؛ يكتبها المالك في الجلسة مباشرة. قاعدة: كل إجراء للمالك برابط مباشر وخطوات مرقمة.
- أكلات جدتنا: طلب الهيدر/مائدة الأسرة في جلسة «الأسر المنتجة» (27 مستودعًا، تكلفة عالية — اقتُرح جلسة جديدة على aser وحده).

## مقترحات لم تُنفّذ
- أدوات GitHub: Renovate وTrivy وOSV-Scanner وLighthouse CI لكل مشروع (عبر جلسة المشروع وبموافقة المالك).
- أدوات الخادم: Uptime Kuma أولًا، ثم CrowdSec وBeszel (عبر جلسة الخادم وCOORDINATION.md وبموافقة المالك).
