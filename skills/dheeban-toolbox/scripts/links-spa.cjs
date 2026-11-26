// فحص روابط تطبيق صفحة واحدة (SPA) بعد التصيير: يفتح الصفحات ويجمع <a> من DOM ثم يفحص كل رابط داخلي مرة واحدة (قراءة فقط).
// الاستعمال: node links-spa.cjs URL [أقصى_صفحات=25]
const { execSync } = require('child_process'); const path = require('path');
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), 'playwright'));
(async () => { const root = new URL(process.argv[2]); const max = +process.argv[3] || 25; const px = process.env.HTTPS_PROXY;
  const b = await chromium.launch(px ? { proxy: { server: px } } : {}); const ctx = await b.newContext(); const p = await ctx.newPage();
  const seen = new Set(), q = [root.href], bad = [], ext = new Map(); let n = 0;
  while (q.length && n < max) { const u = q.shift(); if (seen.has(u)) continue; seen.add(u); n++;
    const r = await p.goto(u, { waitUntil: 'networkidle', timeout: 60000 }).catch(() => null);
    if (!r || r.status() >= 400) { bad.push([r ? r.status() : 0, u, 'صفحة']); continue; }
    const hs = await p.$$eval('a[href]', as => as.map(a => a.href));
    for (const h of hs) { const x = new URL(h); if (!/^https?:$/.test(x.protocol)) continue; x.hash = '';
      if (x.host === root.host) { if (!/\.(css|js|png|jpe?g|svg|ico|webp|woff2?|json|xml|pdf)$/i.test(x.pathname) && !seen.has(x.href)) q.push(x.href); } else ext.set(x.href, u); } }
  const rq = ctx.request; for (const [a, src] of [...ext].slice(0, 40)) { let s = 0; try { s = (await rq.head(a, { timeout: 15000 })).status(); if ([403, 405].includes(s)) s = (await rq.get(a, { timeout: 15000 })).status(); } catch {} if ((s >= 400 && s !== 429) || !s) bad.push([s, a, 'خارجي من ' + src]); }
  console.log(`صفحات مفحوصة: ${n} | روابط خارجية: ${ext.size} | معطوبة: ${bad.length}`); bad.forEach(x => console.log(...x)); await b.close(); })();
