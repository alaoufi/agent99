// فحص الوصولية بـ axe عبر Playwright المثبت مسبقًا. الاستعمال: node a11y.cjs URL
const { execSync } = require('child_process'); const path = require('path'); const os = require('os');
const dir = path.join(os.tmpdir(), 'dheeban-axe');
try { require.resolve(path.join(dir, 'node_modules/@axe-core/playwright')); } catch { execSync(`npm i -s --prefix ${dir} @axe-core/playwright@4`, { stdio: 'ignore' }); }
const { chromium } = require(path.join(execSync('npm root -g').toString().trim(), 'playwright'));
const { AxeBuilder } = require(path.join(dir, 'node_modules/@axe-core/playwright'));
(async () => { const b = await chromium.launch(); const c = await b.newContext(); const p = await c.newPage();
  await p.goto(process.argv[2]); const r = await new AxeBuilder({ page: p }).analyze();
  for (const v of r.violations) console.log(`${v.impact}\t${v.id}\t${v.nodes.length} عنصر\t${v.help}`);
  console.log(`المجموع: ${r.violations.length} نوع مخالفة`); await b.close(); })();
