# تقرير فحص trbhh.sa (تربح — مستودع alaoufi/Trbhh) — 2026-11-26

**النطاق:** فحص حي للقراءة فقط: بلا دخول ولا نماذج ولا ضغط. الصفحات: `/` و`/classified` و`/companies` و`/ads/3639` و`/pages/faq`.
**الأدوات (dheeban-toolbox):** Lighthouse 12 (جوال وكمبيوتر)، axe، weight.cjs، links.py، headers.sh.
**تنبيه قياس:** الحاوية تمر عبر وكيل خروج يُضيف زمن استجابة؛ قارن نسبيًا وأعد القياس المطلق من Actions. لا لقطات شاشة؛ الدليل أرقام وملفات خام في `raw/`.
**لم يُفحص:** شهادة SSL (الوكيل يعترضها)، ولا lychee (مرحلة ثانية).

## الخلاصة
الصفحات الداخلية سريعة (جوال 98 في `/classified` و`/companies`)، لكن **الرئيسية** ثقيلة: HTML بحجم 359KB، 39 صورة 38 منها بلا أبعاد فيصل CLS إلى 0.271، وTBT 600ms على الجوال. وهناك فجوات SEO (canonical وmeta description) وترويسات أمان ناقصة.

| الصفحة | جوال: أداء | LCP | TBT | كمبيوتر: أداء | CLS كمبيوتر |
|---|---|---|---|---|---|
| / | 72 | 3.3ث | 600ms | 80 | 0.271 |
| /classified | 98 | 1.3ث | 130ms | 99 | 0 |
| /companies | 98 | 1.5ث | 140ms | 97 | 0 |
| /ads/3639 | 88 | 3.0ث | 250ms | 71 | 0.271 |
| /pages/faq | 98 | 2.1ث | 100ms | 89 | 0 |

## المشاكل (مرتبة بالأولوية)

### 1) عالية — انزياح التخطيط CLS 0.271 في الرئيسية وصفحة الإعلان
- **الدليل:** Lighthouse كمبيوتر: `/` و`/ads/3639` CLS=0.271 (الحد الجيد 0.1)؛ `layout-shifts`: التذييل `body > footer.mt-6` وزر الترويسة `header.sticky button`؛ `raw/weight_.txt`: 39 صورة، 38 بلا `width/height`.
- **الإصلاح:** إضافة `width/height` أو `aspect-ratio` لكل صور الإعلانات والبطاقات، وحجز ارتفاع للتذييل والترويسة قبل وصول المحتوى، وتحميل الشعار `logo-header.png` (85KB PNG) كـ WebP/SVG بأبعاد ثابتة.

### 2) عالية — حمولة الرئيسية وTBT على الجوال
- **الدليل:** HTML الرئيسية 359KB (document=359KB من 1618KB، 62 طلبًا)؛ جوال: LCP 3.3ث وTBT 600ms وSpeed Index 6.3ث؛ `bootup-time`: `2k3165v68m4ck.js` وحده 340ms (73KB، 33% غير مستخدم)؛ سكربتات خارجية (ختم eauthenticate.saudibusiness.gov.sa) تضيف 83KB.
- **الإصلاح:** تقليل عدد الإعلانات المُصيَّرة في الخادم للشاشة الأولى مع تحميل الباقي بالتمرير (لا ترسل 359KB HTML)، تأخير ختم السجل التجاري (iframe/سكربت) إلى ما بعد التحميل (`loading=lazy`/عند التمرير)، تقسيم JS.

### 3) متوسطة — SEO: canonical وmeta description مفقودان
- **الدليل:** SEO=92 (بدل 100) في `/classified` و`/companies` و`/pages/faq` (canonical غائب) وفي `/ads/3639` (meta description غائب).
- **الإصلاح:** أضف `alternates.canonical` وميتا وصفية لكل مسار ديناميكي (`generateMetadata` في Next) — الوصف من نص الإعلان نفسه؛ والنصوص تُدار من «نصوص الموقع».

### 4) متوسطة — وصولية
- **الدليل:** axe: `color-contrast` في الرئيسية (`p.text-xs.text-muted-foreground` #5e7387 على #f3f4f6 = 4.46 من 4.5)؛ `label-content-name-mismatch` لبطاقة إعلان بـ `aria-label` لا يحتوي النص المرئي (مثل «سيزر لفت مانلفت للايجار…»)؛ `list`: `ul.space-y-3` في `/ads/3639` يحوي عناصر غير `li`؛ `heading-order`: `h4` في التذييل في `/classified` و`/pages/faq` و`/companies`؛ `region` في كل الصفحات.
- **الإصلاح:** غمّق `muted-foreground` قليلًا؛ اجعل `aria-label` يبدأ بنص العنوان المرئي أو احذفه؛ اجعل أبناء `ul` عناصر `li` فقط؛ استعمل مستوى h3 أو h2 في التذييل.

### 5) متوسطة — ترويسات الأمان
- **الدليل:** `raw/headers.txt`: ناقصة `Cross-Origin-Opener-Policy` و`Cross-Origin-Resource-Policy`؛ HSTS بلا `includeSubDomains`؛ CSP واسعة: `script-src 'unsafe-inline'`، `img-src https: http:` (يسمح بـ http)، `connect-src 'self' https: wss:` (أي مضيف). الكوكي `trbhh_vid` سليم (Secure, HttpOnly, SameSite=Lax).
- **الإصلاح:** إضافة COOP `same-origin-allow-popups` (بسبب نافذة الختم/الدخول) وCORP، إزالة `http:` من img/media، تضييق `connect-src` للمضيفات اللازمة (facebook/tiktok/gtm)، وترحيل `unsafe-inline` إلى nonce.

### 6) منخفضة — مشكلة كوكي طرف ثالث (Inspector issue)
- **الدليل:** Best Practices 96: `inspector-issues` نوع Cookie من `eauthenticate.saudibusiness.gov.sa/EAuthSealApi/seal.js`؛ وخطوطها IBMPlexSansArabic بصيغة TTF غير مضغوطة.
- **الإصلاح:** خارج سيطرتنا؛ حمّل الختم متأخرًا وأبقِه في iframe مستقل. وثّق للمالك أنه قيد من الجهة المانحة.

### 7) معلومة — bf-cache وخطوط
- **الدليل:** `cache-control: no-store` يعطّل bf-cache. الخطوط المحلية (woff2 33KB+30KB) جيدة؛ يمكن تقليصها بـ `fonts-subset.sh`.

## ما سلم
الروابط: 40 صفحة داخلية و18 خارجية بلا معطوب (`raw/links.txt`). لا أخطاء كونسول ولا طلبات فاشلة. وصولية Lighthouse 96–98. صفحات `/classified` و`/companies` ممتازة (98+).
