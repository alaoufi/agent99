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

## مقترحات لم تُنفّذ
- أدوات GitHub: Renovate وTrivy وOSV-Scanner وLighthouse CI لكل مشروع (عبر جلسة المشروع وبموافقة المالك).
- أدوات الخادم: Uptime Kuma أولًا، ثم CrowdSec وBeszel (عبر جلسة الخادم وCOORDINATION.md وبموافقة المالك).
