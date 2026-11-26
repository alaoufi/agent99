#!/usr/bin/env python3
"""فحص الروابط المكسورة (قراءة فقط، متتابع وبمهلة): يقرأ صفحات الموقع الداخلية حتى عمق N ويفحص كل رابط داخلي وخارجي.
بديل خفيف إلى أن يُثبَّت lychee (انظر SKILL.md). الاستعمال: python3 links.py https://site [أقصى_صفحات=40] [تأخير_ثوانٍ=0.2]"""
import sys, re, time, urllib.parse, urllib.request, ssl
root = sys.argv[1].rstrip('/'); maxp = int(sys.argv[2]) if len(sys.argv) > 2 else 40; delay = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
host = urllib.parse.urlparse(root).netloc; UA = {'User-Agent': 'dheeban-linkcheck/1.0 (read-only)'}
def get(u, method='GET'):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers=UA, method=method), timeout=20); return r.status, r.read(2_000_000).decode('utf-8', 'ignore') if method == 'GET' else ''
    except urllib.error.HTTPError as e: return e.code, ''
    except Exception as e: return 0, str(e)[:60]
seen, queue, pages, bad, ext = set(), [root + '/'], 0, [], {}
while queue and pages < maxp:
    u = queue.pop(0)
    if u in seen: continue
    seen.add(u); s, body = get(u); pages += 1; time.sleep(delay)
    if s >= 400 or s == 0: bad.append((s, u, 'صفحة')); continue
    for h in re.findall(r'<a\s[^>]*?href=["\']([^"\'#\s]+)', body):
        a = urllib.parse.urljoin(u, h).split('#')[0]; p = urllib.parse.urlparse(a)
        if p.scheme not in ('http', 'https'): continue
        if p.netloc == host:
            if not re.search(r'\.(css|js|png|jpe?g|svg|ico|webp|woff2?|json|xml|webmanifest|pdf)(\?|$)', p.path) and a not in seen: queue.append(a)
        else: ext.setdefault(a, u)
for a, src in list(ext.items())[:60]:
    s, _ = get(a, 'HEAD'); 
    if s in (403, 405, 0): s, _ = get(a)
    time.sleep(delay)
    if (s >= 400 and s != 429) or s == 0: bad.append((s, a, 'خارجي من ' + src))
print(f'صفحات مفحوصة: {pages} | روابط خارجية: {len(ext)} | معطوبة: {len(bad)}')
for s, a, w in bad: print(s, a, w)
