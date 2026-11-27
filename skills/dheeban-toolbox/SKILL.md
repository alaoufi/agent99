---
name: dheeban-toolbox
description: صندوق أدوات ذيبان المجانية المجرَّبة - قياس سرعة الموقع (Lighthouse/Unlighthouse/LHCI)، الوصولية (axe)، الروابط المكسورة، ترويسات الأمان، حجم الصفحة والخطوط والصور، كود غير مستخدم (knip)، حدود الحجم (size-limit)، تقليص الخطوط العربية، فحص أندرويد (mobsfscan)، اختبار التحمل للنسخ المحلية، الثغرات (semgrep، npm audit، secretlint)، وأدوات الخادم وGitHub، وخطة التحليلات والمالية والتسويق. استخدمه عند طلب فحص سرعة أو تحمل أو أمان أو وصولية أو تقرير احترافي لأي مشروع.
---

# صندوق أدوات ذيبان (مجاني، بلا اشتراكات، مجرَّب في 2026-11-25)

كل الأدوات تعمل عند الطلب بـ npx/pip **دون تثبيت دائم**. السكربتات في `scripts/` بجانب هذا الملف.
**لا تختبر الإنتاج بالضغط** إلا بإذن المالك: الضغط على موقع حي قد يوقفه. اختبر نسخة محلية أو تجريبية.
الشبكة: مواقع المالك الخارجية قد تكون محجوبة في بيئة Default؛ شغّل الخادم محليًا واختبر `http://127.0.0.1:PORT`.

**الحالة:** ✅ جُرّب فعليًا في حاوية ذيبان (2026-11-26) · 🅰 مجرَّب في GitHub Actions (2026-11-27) ولا يُشغَّل في الحاوية (المصنِّف يمنع تشغيل الثنائيات المنزّلة) · ⏳ لم يُجرَّب بعد.
**داخل حاوية ذيبان** يمر Chromium عبر وكيل الخروج (`HTTPS_PROXY`) تلقائيًا في سكربتاتنا؛ Lighthouse الخام يحتاج `--proxy-server=$HTTPS_PROXY` وإلا يفشل بـ NO_NAVSTART. أحيانًا تفشل صفحة بـ NO_NAVSTART: أعد التشغيل.
**حمل النتائج:** لا تشغّل أداة ثقيلة بالتوازي مع Lighthouse، فالدرجات تتأثر بحمل المعالج.

| الحاجة | الأمر | الحالة | أين تعمل |
|---|---|---|---|
| السرعة وSEO وأفضل الممارسات (صفحة) | `bash scripts/speed.sh URL [OUT]` (كمبيوتر: `LH_EXTRA=--preset=desktop`) | ✅ | الحاوية / Actions |
| كل صفحات الموقع دفعة واحدة | `bash scripts/unlighthouse.sh URL [OUT]` (Unlighthouse 0.16.1) | ✅ على نسخة محلية؛ على الحي حدّد الصفحات | الحاوية / Actions |
| حدود جودة تفشل البناء | `bash scripts/lhci.sh URL...` + `lighthouserc.json` (LHCI 0.15.1) | ✅ | Actions (الأنسب) / الحاوية |
| الوصولية | `node scripts/a11y.cjs URL` | ✅ | الحاوية / Actions |
| وزن الصفحة والخطوط والصور وأخطاء الكونسول | `node scripts/weight.cjs URL` | ✅ | الحاوية |
| الروابط المكسورة (SSR) | `python3 scripts/links.py URL [صفحات] [تأخير]` | ✅ بديل خفيف | الحاوية |
| الروابط المكسورة (SPA/React) | `node scripts/links-spa.cjs URL [صفحات]` | ✅ | الحاوية |
| الروابط المكسورة (الأداة الكاملة) | `lychee --no-progress URL` (lychee v0.20.1) | 🅰 Actions | Actions (`lycheeverse/lychee-action`) / الحاوية |
| ترويسات الأمان وHSTS وإعادة HTTP→HTTPS | `bash scripts/headers.sh URL` | ✅ (فحص شهادة SSL لا يصح من الحاوية: الوكيل يعترضها؛ افحصها من الخادم) | الحاوية / الخادم |
| كود وتبعيات وملفات غير مستخدمة | `bash scripts/deadcode.sh DIR` (knip 5.61.0 + typescript) | ✅ | الحاوية |
| حدود حجم الحزمة (JS/CSS) | `npm i -D size-limit@11.2.0 @size-limit/file@11.2.0` ثم `npx size-limit` مع `.size-limit.json` (المُلحق يجب أن يكون في المشروع نفسه) | ✅ | Actions / الحاوية |
| تقليص الخطوط العربية | `bash scripts/fonts-subset.sh cairo 400 OUT` (Fontsource + fonttools 4.58.4) | ✅ | الحاوية |
| أسرار في تاريخ git كامل | `gitleaks git --redact -v .` (Gitleaks v8.28.0) | 🅰 Actions. في الحاوية: `security.sh` (secretlint على الملفات الحالية) | Actions (`gitleaks-action`) / الحاوية |
| التحمل (ضغط) — **نسخ محلية فقط** | `bash scripts/load.sh URL [اتصالات] [ثوانٍ]` ؛ سيناريوهات: `k6 run ci/k6-smoke.js` (k6 v1.0.0) | load.sh ✅ · k6 🅰 Actions | الحاوية (127.0.0.1) |
| تحليل Dockerfile | `hadolint Dockerfile` (hadolint v2.12.0) | 🅰 Actions | Actions (`hadolint-action`) / الحاوية |
| أندرويد (كود المصدر) | `bash scripts/mobsf.sh DIR` (mobsfscan 0.4.5) | ✅ يعمل؛ جُرّب على مقتطف صغير فأعطى INFO فقط، فاختبره على مشروع حقيقي | الحاوية |
| تقرير تطبيق APK كامل | MobSF (انظر أدوات الخادم) | ⏳ | الخادم |
| ثغرات الكود | `bash scripts/security.sh DIR` | ✅ | الحاوية |

التنزيل الثنائي: `https://github.com/<org>/<repo>/releases/download/<الإصدار>/...` يعمل عبر الوكيل، لكن `releases/latest` وapi.github.com محجوبان؛ **ثبّت الإصدار دائمًا**.

## مكتبة Semgrep العامة
`semgrep --config p/...` يحتاج المضيف `semgrep.dev` (محجوب الآن). استخدم قواعد المشروع المحلية (مثل `Trbhh/security/semgrep-local.yml`)، أو اطلب من المالك إضافة المضيف عند الحاجة.

## أدوات خارج الحاوية (تُركَّب في المشروع نفسه، مجانية)
- **سلوك العملاء وما يحبون:** PostHog (مسارات، تسجيل جلسات، تجارب A/B؛ مجاني حتى مليون حدث شهريًا، أو استضافة ذاتية) أو Microsoft Clarity (خرائط حرارية مجانية). لـ PostHog موصل جاهز في Claude يقرأ البيانات ويقترح.
- **إحصاءات الزوار بخصوصية:** Umami أو Plausible باستضافة ذاتية على خادم المشروع.
- **الأخطاء الحية:** Sentry (طبقة مجانية) وله موصل في Claude.
- **تنظيم القوائم والجداول في الواجهات:** TanStack Table (فرز/تصفية/تقسيم صفحات) و dnd-kit (سحب وإفلات للترتيب) — مكتبات مجانية.
- **التقارير المالية:** مهارة xlsx/pdf الموجودة + إضافة Finance من Anthropic؛ لا تربط بوابة دفع حقيقية بلا إذن المالك.

## تقرير احترافي
بعد أي فحص: لخّص بالعربية (الدرجة، أهم 5 مشاكل، الإصلاح المقترح لكل منها، الأولوية) واحفظ المخرجات في `docs/reports/` بالمشروع.

## أدوات الخادم (تُركّب عبر جلسة الخادم بموافقة المالك وCOORDINATION.md)
لا تُركَّب من ذيبان ولا من جلسات المشاريع. يطلب ذيبان عبر Issue `[server-edge]` في `alaoufi/server-edge` وفق COORDINATION.md، والمالك يوافق. كلها مجانية ومفتوحة المصدر.
| الأداة | الفائدة |
|---|---|
| Uptime Kuma | مراقبة توفر المواقع والمنافذ وتنبيهات فورية (واتساب/تيليجرام/بريد) وصفحة حالة |
| CrowdSec | حظر آلي للمهاجمين من سجلات Caddy/SSH بقواعد مجتمعية |
| Beszel | مراقبة خفيفة للمعالج والذاكرة والقرص والحاويات |
| GlitchTip | تتبع أخطاء متوافق مع Sentry SDK باستضافة ذاتية |
| PgHero | استعلامات بطيئة وفهارس ناقصة وحجم قواعد PostgreSQL |
| Lynis | تدقيق تقوية نظام Linux (يُشغَّل دوريًا ويُراجَع) |
| Docker Bench for Security | فحص إعدادات Docker مقابل CIS |
| MobSF | تحليل ساكن/ديناميكي لتطبيقات APK/IPA (ثقيل: يُشغَّل عند الحاجة ويُطفأ) |

## GitHub (تُضاف إلى مستودع المشروع عبر جلسته الرسمية وبموافقة المالك، لا من ذيبان)
| الأداة | الفائدة |
|---|---|
| Renovate (أو Dependabot) | طلبات دمج تلقائية لتحديث التبعيات |
| Trivy | ثغرات التبعيات والحاويات وملفات Dockerfile/IaC |
| OSV-Scanner | ثغرات التبعيات من قاعدة OSV (يقرأ ملفات lock) |
| Lighthouse CI | حدود أداء/وصولية تفشل الطلب إن تراجعت (`scripts/lhci.sh` نفسه) |
| Gitleaks / lychee / hadolint / k6 | أسرار، روابط، Dockerfile، تحمل — انسخ خطوات `.github/workflows/toolbox-phase2.yml` من agent99 |

## المرحلة الثانية: Gitleaks وlychee وhadolint وk6 (2026-11-27)
- المصدر: GitHub Releases الرسمية بإصدارات مثبتة، والتنزيل يتحقق من SHA-256 في `scripts/fetch-bins.sh` (المجاميع من ملفات المجاميع الرسمية؛ lychee لا ينشر ملفًا فسُجّل مجموعه عند أول تنزيل).
- التنزيل والتحقق نجحا في الحاوية، لكن **المصنِّف يمنع تشغيل الثنائيات المنزّلة** فيها. فلا تحاول الالتفاف: شغّلها في GitHub Actions.
- التجربة: سير العمل `.github/workflows/toolbox-phase2.yml` في agent99 (يدوي من تبويب Actions أو عند تعديل الصندوق). يشغّل Gitleaks على تاريخ git، وhadolint على `ci/Dockerfile.sample` (عيّنة مقصودة الأخطاء)، وlychee على ملفات Markdown ورابط خارجي، وk6 بـ `ci/k6-smoke.js` على خادم محلي.
- نتيجة أول تشغيل (run 45988662914): المجاميع طابقت، Gitleaks: 34 commit بلا تسريب، hadolint: 6 ملاحظات متوقعة على العيّنة، k6: 250 طلبًا 0% فشل p95=2.8ms، lychee: يعمل (أُصلح نمط ملفات Markdown بعد أن فحص 0 ملف).
- لمشروع: انسخ الخطوات اللازمة إلى سير عمل المشروع عبر جلسته الرسمية وبرومبت يلصقه المالك. بدائل جاهزة: `gitleaks/gitleaks-action@v2` و`lycheeverse/lychee-action@v2` و`hadolint/hadolint-action@v3.1.0` و`grafana/setup-k6-action@v1` (ثبّت الإصدار).
