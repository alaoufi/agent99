# جرد الأدوات والمهارات (2026-11-25، بيئة Default السحابية) — لا تُعِد تثبيت شيء مما هنا

## على مستوى الحساب (تتزامن تلقائيًا لكل جلسة، مصدرها claude.ai)
- مهارات (21): banner-design, brand, built-in-browser, chrome-browser, computer-use, deep-research, design, design-system, docs, docx, google-workspace, import-memory, morning, pdf, pptx, skill-creator, slides, ui-styling, ui-ux-pro-max, xlsx.
- إضافات: superpowers (خطاف SessionStart + مهارات العمليات)، cowork-plugin-management، twilio-developer-kit (~60 مهارة + خادم MCP يفشل: مضيفه محجوب 403).
- موصلات MCP: GitHub, Figma, Neon, Render, Vercel, Claude Docs (تعمل)؛ Supabase (يحتاج تفويضًا).

## مدمج في الحاوية
- claude 2.1.x، node 22، python3، gh (للبحث فقط)، Playwright + Chromium (/opt/pw-browsers/chromium)، bun، cargo.
- لا يوجد Codex CLI في الحاوية؛ كودكس يعمل من جهته ويتنسق عبر GitHub.

## على مستوى المشاريع (تبقى في مستودعاتها، لا تُنقل للعام)
- teachabs: وكيل routine + مهارات gsap-* + أذونات.
- Trbhh: خطاف semgrep بعد التعديل. aser: Playwright MCP في .mcp.json.
- Alaoufi.me, Almfrje: أذونات قراءة PR.
- AGENTS.md في: Trbhh, agar, aser, aykdmah.

## بيئات سحابية أخرى
- aykdmh (شبكة مفتوحة، له سكربت إعداد خاص)، saud (محدودة، بلا سكربت). ذيب يُفعَّل فيها بإضافة سكربته لها من جلسة تعمل عليها.

## توصيات بلا تثبيت
1. إن لم تُستخدم Twilio: عطّل إضافة twilio-developer-kit من claude.ai (توفّر ~60 وصف مهارة في كل جلسة + محاولة MCP فاشلة).
2. فوّض الأعمال الروتينية لوكلاء بنموذج أخف (كما في teachabs/routine وdheeb).
