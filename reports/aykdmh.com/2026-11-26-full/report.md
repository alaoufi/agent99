# تقرير فحص aykdmh.com (أي خدمة — مستودع alaoufi/aykdmah) — 2026-11-26

**النطاق:** فحص حي للقراءة فقط: بلا دخول ولا نماذج ولا ضغط. الصفحات: `/` و`/services` و`/services/1` و`/guide` و`/register`.
**الأدوات (dheeban-toolbox):** Lighthouse 12 (جوال وكمبيوتر)، axe، weight.cjs، links-spa.cjs (الموقع SPA)، headers.sh.
**تنبيه قياس:** الحاوية تمر عبر وكيل خروج يُضيف زمن استجابة (TTFB 1.3ث في الرئيسية قد يكون بعضه من الوكيل)؛ الفروق النسبية بين الصفحات والأوزان صحيحة، والأزمنة المطلقة تُعاد من Actions. لا لقطات شاشة؛ الدليل أرقام وملفات خام في `raw/`.
**لم يُفحص:** شهادة SSL (الوكيل يعترضها)، ولا lychee (مرحلة ثانية).

## الخلاصة
أضعف المواقع الثلاثة على الجوال: أداء 47–67 وLCP 5.4–6.2ث. السببان الأكبران قابلان للإصلاح بسرعة: صور مقدّمي الخدمة تُقدَّم بحجم 1600px وهي تُعرض بـ40px (3.1MB هدر في الرئيسية)، وحزمة JS واحدة كبيرة. الأمان ممتاز (كل الترويسات الثمانية). وهناك خطأ حقيقي في روابط واتساب (نطاق خاطئ).

| الصفحة | جوال: أداء | LCP | TBT | CLS | كمبيوتر: أداء |
|---|---|---|---|---|---|
| / | 47 | 6.0ث | 400ms | 0.164 | 89 (CLS 0.115) |
| /services | 52 | 5.7ث | 600ms | 0.044 | 82 |
| /services/1 | 62 | 6.2ث | 150ms | 0.019 | 85 |
| /guide | 49 | 5.4ث | 830ms | 0 | 88 |
| /register | 67 | 5.7ث | 90ms | 0 | 87 |

## المشاكل (مرتبة بالأولوية)

### 1) عالية — صور مقدّمي الخدمة ضخمة وبلا صيغة حديثة
- **الدليل:** الرئيسية 4790KB (`raw/weight_.txt`): صورة `/api/media/1139625b…` = 2136KB، و`6235551c…` = 585KB، و`1b35341f…` = 269KB. Lighthouse: `image-delivery-insight` هدر 3,147KiB، `uses-responsive-images` 3,124KiB، `modern-image-formats` 2,481KiB؛ العناصر `img.w-10` (40px) والمصدر 1600×1600 و1024×1024؛ 6 من 7 صور أكبر من اللازم أكثر من ضعفين؛ 5 من 7 بلا `width/height`.
- **الإصلاح:** عند الرفع في `/api/media` أنتج نسخًا مصغّرة (مثلًا 96/192/400px) بصيغة WebP/AVIF، وقدّم `srcset/sizes`، واحفظ `width/height`، و`loading="lazy"` لما تحت الشاشة، وكاش طويل (`immutable`) للميديا. الأثر المتوقع: من 3.8MB إلى أقل من 0.8MB.

### 2) عالية — JS ثقيل في حزمة واحدة وTBT مرتفع
- **الدليل:** `index-DOna5eHg.js` = 813KB غير مضغوط (259KB منقول) مع `en-LQ9cK8Jv.js` = 149KB و`react-vendor` = 176KB؛ scripts إجمالي 1331–1538KB؛ TBT 830ms في `/guide` و600ms في `/services`؛ `unused-javascript` 43KiB؛ `valid-source-maps`: «ملف JS كبير بلا source map».
- **الإصلاح:** تقسيم المسارات (React.lazy/route-level code splitting)، ألا تُحمَّل لغة ثانية (`en-*.js`) إلا عند الطلب، فحص حجم الحزمة بـ `size-limit` (مثلًا 150KB للمسار الأول) في CI، وتوليد source maps للإنتاج مع حجبها عن العامة أو رفعها لأداة الأخطاء.

### 3) عالية — بطء العرض الأول على الجوال (FCP 4.4–5.3ث)
- **الدليل:** `lcp-breakdown`: TTFB 1343ms في الرئيسية، `render-blocking-insight` توفير 300ms (CSS 25KB وregisterSW.js)، وعنصر LCP نص داخل `a.min-w-0 > span.block` (يتأخر لأن التطبيق SPA يرسم من JS).
- **الإصلاح:** تحميل CSS الحرج مضمّنًا، تأجيل `registerSW.js`، تقديم هيكل الصفحة (skeleton) فورًا، وإن أمكن توليد الصفحات العامة مسبقًا (prerender/SSR) للرئيسية و`/services` و`/guide`.

### 4) متوسطة — انزياح التخطيط (CLS) في الرئيسية
- **الدليل:** CLS 0.164 جوال و0.115 كمبيوتر؛ عنصر الانزياح `footer.site-footer` (يتحرك لما تصل البيانات).
- **الإصلاح:** حجز ارتفاع للقوائم قبل وصول البيانات (`min-height`/skeleton) وأبعاد للصور.

### 5) متوسطة — روابط واتساب تحمل نطاقًا خاطئًا، ورابط تيليجرام مشوَّه
- **الدليل:** `raw/links.txt`: نص رسالة واتساب الجاهز يحوي `via Ay Khidma: https://aykdmh.sa/providers/18` و`.../services` و`.../requests/new` و`.../guide` (النطاق `aykdmh.sa` بدل `aykdmh.com`)؛ وفي الصفحة `/api/verified` رابط `https://http//t.me/saud050078` (مشوَّه ولن يفتح).
- **الإصلاح:** اجعل أساس الرابط من متغير واحد (`SITE_URL`) بدل نص ثابت، وصحّح رابط تيليجرام إلى `https://t.me/saud050078`. تأكد من المالك أن `aykdmh.sa` ليس نطاقًا مقصودًا. (روابط أخرى ظهرت بحالة 0/400/403 — business.sa وyoutube وx.com وfacebook وwa.me/qr — **غير مؤكدة**: غالبًا حجب روبوتات أو الوكيل؛ أعد فحصها بـ lychee من Actions.)

### 6) متوسطة — وصولية: تباين الألوان واسم الوصول
- **الدليل:** `color-contrast`: نص `text-slate-500` (#425a70) على `bg-cream` (#dcc7a3) = 4.35 (المطلوب 4.5) في `/services` (5 عناصر) و`/guide` (2) و`/register` (1)؛ `label-content-name-mismatch` في شارات المتاجر (Android intent وApp Store) وشارة `ayk-sbc-badge`؛ `page-has-heading-one` ناقص في الرئيسية؛ `link-in-text-block` في `/register` (روابط تعتمد اللون وحده)؛ `region` في كل الصفحات.
- **الإصلاح:** غمّق اللون إلى `slate-600` فأعلى؛ اجعل `aria-label` يبدأ بالنص المرئي؛ أضف `h1` للرئيسية؛ أضف تسطيرًا للروابط داخل النص؛ ضع المحتوى في landmarks.

### 7) منخفضة — خطوط من Google
- **الدليل:** `weight_.txt`: inter (47KB) وcairo (33KB) من `fonts.gstatic.com`، وCSP يسمح بـ`fonts.googleapis.com`.
- **الإصلاح:** استضافة Cairo محليًا وتقليصه للعربية بـ `scripts/fonts-subset.sh` (أصغر وأسرع وخصوصية أفضل)، وحذف Inter إن لم يلزم.

### 8) منخفضة — ترويسات التخزين
- **الدليل:** `cache-control` مكرر في الاستجابة (`no-cache, no-store, must-revalidate` ثم `no-cache`)؛ `bf-cache` يفشل.
- **الإصلاح:** ترويسة واحدة؛ ملفات `/assets/*` المُجزّأة بالهاش `immutable, max-age=31536000`.

## ما سلم
ترويسات الأمان الثمانية كلها موجودة (HSTS مع includeSubDomains، CSP صارم `script-src 'self'`، CORP/COOP). لا أخطاء كونسول ولا طلبات فاشلة. Best Practices 100 وSEO 100 في كل الصفحات. إعادة HTTP→HTTPS تعمل.
