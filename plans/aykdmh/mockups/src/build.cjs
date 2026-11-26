// يولّد صفحات HTML للقالب «المبسّط» ثم يلتقط PNG. للتصوّر فقط — ليس كود الموقع.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
const ROOT=path.resolve(__dirname,'..');
const THEMES={
 identity:{n:'الهوية الحالية',bg:'#FAF7F2',surface:'#FFFFFF',text:'#0B2D56',muted:'#5B6B80',primary:'#A45130',primaryFg:'#FFFFFF',sand:'#DCC7A3',soft:'#F1E7D6',border:'#E6DCCB',accent:'#1E7BE0',ok:'#0F7A4D',chipBg:'#FFFFFF'},
 calm:{n:'هادئ',bg:'#F3F6F4',surface:'#FFFFFF',text:'#1E2D2B',muted:'#5A6B67',primary:'#3F6B5E',primaryFg:'#FFFFFF',sand:'#CFDDD7',soft:'#E4EDE9',border:'#D7E1DC',accent:'#2B6A9A',ok:'#1F7A55',chipBg:'#FFFFFF'},
 dark:{n:'ليلي داكن',bg:'#14110F',surface:'#201B18',text:'#F3EBDD',muted:'#B7AA98',primary:'#E0895F',primaryFg:'#1A0E08',sand:'#4A3A2E',soft:'#2A231E',border:'#3A312A',accent:'#7DB8F7',ok:'#5FD39B',chipBg:'#201B18'},
 contrast:{n:'تباين عالٍ',bg:'#FFFFFF',surface:'#FFFFFF',text:'#000000',muted:'#2B2B2B',primary:'#7A2E12',primaryFg:'#FFFFFF',sand:'#000000',soft:'#F2F2F2',border:'#000000',accent:'#0043A8',ok:'#005A32',chipBg:'#FFFFFF'}
};
const L={ar:{
 dir:'rtl',lang:'ar',font:"'Cairo',system-ui,sans-serif",name:'أي خدمة',
 tpl:'القالب',classic:'الكلاسيكي',simple:'المبسّط',
 h1:'اطلب خدمتك، واستقبل عروضًا من فنيين قريبين منك',sub:'اكتب طلبك مجانًا في دقيقة، وقارن، ثم تواصل مع من يناسبك.',
 need:'أحتاج',inCity:'في',needPh:'مثال: كهربائي، سباك، تكييف',cityPh:'مدينتي',search:'ابحث',post:'أو اكتب طلبك مجانًا',
 chips:['صيانة منزلية','نظافة','نقل وعفش','كهرباء','سباكة','تكييف وتبريد'],
 trustT:'لماذا تثق بالنتائج',t1:'شارة «موثّق» تظهر فقط على الحسابات الموثّقة',t2:'التقييمات تظهر باسم المقيِّم وتاريخها',t3:'تصفّح بلا تسجيل، وتواصل مباشرة بالمحادثة أو الاتصال',
 provs:'من مقدمي الخدمة',real:'من بيانات الموقع',cat1:'كهرباء',cat2:'صيانة منزلية',cityA:'المجمعة',cityB:'المستقبل',
 rated:'تقييم',one:'تقييم واحد',chat:'محادثة',call:'اتصال',verified:'موثّق',avail:'متاح للعمل',
 nav:['الرئيسية','الخدمات','اطلب','المحادثات','حسابي'],
 foot:'أي خدمة فرع من موقع تربح',verifiedStore:'متجر موثّق',
 exampleBadge:'مثال توضيحي',
 pName:'كهربائي وسباك المجمعه',pDesc:'جميع اعمال السباكه والكهرباء',pCity:'المجمعة',pRange:'يقدّم الخدمة ضمن 25 كم من المجمعة',pRangeNote:'الموقع الدقيق يظهر بعد قبول الطلب',
 done:'طلبات مكتملة: 2',reviews:'آراء طالبي الخدمة',rv:'فني ممتاز',rvName:'أبو ماجد',rvAgo:'قبل 6 أيام',share:'مشاركة',save:'أضف إلى دليلي',
 resTitle:'نتائج «كهرباء» في المجمعة',resCount:'نتيجة',filters:['كل الأحياء','الأعلى تقييمًا','متاح الآن'],
 near:'قريب منك',noRate:'لا تقييمات بعد',
 emptyT:'ما وجدنا «زززقق» في المجمعة',emptyP:'لا تقلق، عندك ثلاث خطوات سريعة:',
 e1:'جرّب كلمة أبسط، مثل «كهرباء» بدل اسم محدد',e2:'وسّع البحث إلى كل المدن',e3:'اكتب طلبك مجانًا ليصل إلى الفنيين المناسبين',
 e1b:'غيّر الكلمة',e2b:'كل المدن',e3b:'اكتب طلبك مجانًا',browse:'أو تصفّح الأقسام',
 },en:{
 dir:'ltr',lang:'en',font:"'Inter',system-ui,sans-serif",name:'Ay Khidma',
 tpl:'Layout',classic:'Classic',simple:'Simple',
 h1:'Post what you need and get offers from providers near you',sub:'Write your request free in a minute, compare, then contact the one you like.',
 need:'I need',inCity:'in',needPh:'e.g. electrician, plumber, A/C',cityPh:'my city',search:'Search',post:'Or post your request for free',
 chips:['Home maintenance','Cleaning','Moving','Electrical','Plumbing','A/C & cooling'],
 trustT:'Why you can trust the results',t1:'The “Verified” badge appears only on verified accounts',t2:'Ratings show the reviewer’s name and date',t3:'Browse without signing up, contact by chat or phone',
 provs:'Service providers',real:'From the site’s data',cat1:'Electrical',cat2:'Home maintenance',cityA:'Al Majmaah',cityB:'Al Mustaqbal',
 rated:'rating',one:'1 rating',chat:'Chat',call:'Call',verified:'Verified',avail:'Available',
 nav:['Home','Services','Request','Chats','Account'],
 foot:'Ay Khidma is a branch of Trbhh',verifiedStore:'Verified store',
 exampleBadge:'Illustrative example',
 pName:'كهربائي وسباك المجمعه',pDesc:'جميع اعمال السباكه والكهرباء',pCity:'Al Majmaah',pRange:'Serves within 25 km of Al Majmaah',pRangeNote:'Exact location appears after the request is accepted',
 done:'Completed requests: 2',reviews:'Customer reviews',rv:'فني ممتاز',rvName:'ابو ماجد',rvAgo:'6 days ago',share:'Share',save:'Add to my guide',
 resTitle:'“Electrical” results in Al Majmaah',resCount:'result',filters:['All areas','Top rated','Available now'],
 near:'Near you',noRate:'No ratings yet',
 emptyT:'We found no “zzzqqq” in Al Majmaah',emptyP:'No problem — three quick ways forward:',
 e1:'Try a simpler word, like “electrical” instead of a name',e2:'Widen the search to all cities',e3:'Post your request free so it reaches the right providers',
 e1b:'Change the word',e2b:'All cities',e3b:'Post your request free',browse:'Or browse categories',
}};
const css=(T,l)=>`
:root{--bg:${T.bg};--s:${T.surface};--t:${T.text};--m:${T.muted};--p:${T.primary};--pf:${T.primaryFg};--sand:${T.sand};--soft:${T.soft};--b:${T.border};--a:${T.accent};--ok:${T.ok};--chip:${T.chipBg}}
*{box-sizing:border-box;margin:0}
body{width:390px;background:var(--bg);color:var(--t);font:15px/1.7 ${l.font};-webkit-font-smoothing:antialiased}
.hdr{display:flex;align-items:center;gap:10px;padding:12px 16px;background:var(--s);border-bottom:1px solid var(--b)}
.hdr img{width:40px;height:40px;border-radius:10px;background:#fff;padding:2px}
.hdr b{font-size:17px;flex:1}
.ic{width:36px;height:36px;border-radius:10px;border:1px solid var(--b);display:grid;place-items:center;font-size:12px;font-weight:700;color:var(--t);background:var(--s)}
.sw{margin:12px 16px 0;display:flex;align-items:center;gap:8px;font-size:13px;color:var(--m)}
.seg{display:flex;border:1px solid var(--b);border-radius:999px;overflow:hidden;background:var(--s)}
.seg span{padding:4px 14px;font-weight:600;font-size:13px}.seg .on{background:var(--p);color:var(--pf)}
main{padding:16px 16px 24px}
h1{font-size:26px;line-height:1.35;font-weight:800;margin:6px 0 6px}
.sub{color:var(--m);margin-bottom:16px}
.card{background:var(--s);border:1px solid var(--b);border-radius:16px;padding:16px;margin-bottom:16px}
.q{font-size:16px;font-weight:700;margin-bottom:6px;display:block}
.f{display:flex;align-items:center;border:1.5px solid var(--sand);border-radius:12px;padding:0 14px;height:50px;margin-bottom:12px;color:var(--m);background:var(--bg)}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;height:52px;border-radius:12px;background:var(--p);color:var(--pf);font-weight:800;font-size:17px;width:100%}
.btn2{display:flex;align-items:center;justify-content:center;height:46px;border-radius:12px;border:1.5px solid var(--p);color:var(--p);font-weight:700;width:100%}
.lnk{display:block;text-align:center;color:var(--a);font-weight:700;margin-top:12px}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:4px}
.chip{border:1px solid var(--sand);background:var(--chip);border-radius:999px;padding:6px 14px;font-weight:600;font-size:14px}
h2{font-size:18px;font-weight:800;margin:20px 0 10px}
.tr{display:flex;gap:10px;align-items:flex-start;padding:6px 0}.tr i{font-style:normal;color:var(--ok);font-weight:800}
.pc{display:flex;gap:12px;align-items:center;background:var(--s);border:1px solid var(--b);border-radius:16px;padding:12px;margin-bottom:10px}
.av{width:52px;height:52px;border-radius:50%;background:var(--soft);display:grid;place-items:center;font-weight:800;color:var(--p);font-size:20px;flex:none}
.pc .i{flex:1;min-width:0}.pc b{display:block;line-height:1.4}.pc small{color:var(--m)}
.st{color:#B45309;font-weight:800;font-size:14px}
.cta{display:flex;gap:8px}.cta span{width:42px;height:42px;border-radius:50%;display:grid;place-items:center;background:var(--p);color:var(--pf);font-size:12px;font-weight:700}
.badge{display:inline-block;border:1px solid var(--ok);color:var(--ok);border-radius:999px;padding:0 8px;font-size:12px;font-weight:700}
.ex{display:inline-block;background:var(--soft);color:var(--m);border-radius:6px;padding:0 8px;font-size:12px;font-weight:600}
.nav{display:flex;justify-content:space-around;background:var(--s);border-top:1px solid var(--b);padding:8px 0;font-size:12px;color:var(--m)}
.nav div{text-align:center}.nav .on{color:var(--p);font-weight:800}.nav .plus{color:var(--pf);background:var(--p);width:40px;height:40px;border-radius:50%;display:grid;place-items:center;font-size:22px;margin-top:-2px}
.ft{padding:16px;font-size:13px;color:var(--m);border-top:1px solid var(--b);text-align:center}
.row{display:flex;justify-content:space-between;gap:8px;padding:8px 0;border-top:1px solid var(--b)}
.step{display:flex;align-items:center;gap:12px;padding:12px 0;border-top:1px solid var(--b)}
.step .n{width:30px;height:30px;border-radius:50%;background:var(--soft);display:grid;place-items:center;font-weight:800;color:var(--p);flex:none}
.step p{flex:1;line-height:1.5}.step a{color:var(--a);font-weight:700;font-size:14px;white-space:nowrap}
.fl{display:flex;gap:8px;overflow:hidden;margin-bottom:12px}
:focus-visible{outline:3px solid var(--a)}
`;
const logo='../assets/logo.webp';
const nav=(l,on)=>`<div class="nav">${['⌂','▦','+','✉','☺'].map((g,i)=>i==2?`<div><div class="plus">+</div></div>`:`<div class="${i==on?'on':''}">${g}<br>${l.nav[i]}</div>`).join('')}</div>`;
const head=(l,th)=>`<div class="hdr"><img src="${logo}" alt=""><b>${l.name}</b><span class="ic">${l.lang=='ar'?'EN':'ع'}</span><span class="ic">${th=='dark'?'☀':'☾'}</span></div>
<div class="sw"><span>${l.tpl}</span><div class="seg"><span>${l.classic}</span><span class="on">${l.simple}</span></div></div>`;
const prov=(l,name,meta,rate,i)=>`<div class="pc"><div class="av">${[...name][0]}</div><div class="i"><b>${name}</b><small>${meta}</small>${rate?`<div class="st">★ ${rate}</div>`:`<div><small>${l.noRate}</small></div>`}</div><div class="cta"><span>${l.chat}</span></div></div>`;
const foot=l=>`<div class="ft"><span class="badge">✓ ${l.verifiedStore}</span><br>${l.foot}</div>`;
const pages={
home:(l)=>`<main><h1>${l.h1}</h1><p class="sub">${l.sub}</p>
<div class="card"><label class="q">${l.need}</label><div class="f">${l.needPh}</div><label class="q">${l.inCity}</label><div class="f">${l.cityPh}</div><div class="btn">${l.search}</div><a class="lnk">${l.post} ←</a></div>
<div class="chips">${l.chips.map(c=>`<span class="chip">${c}</span>`).join('')}</div>
<h2>${l.trustT}</h2><div class="card" style="padding:8px 16px">${[l.t1,l.t2,l.t3].map(t=>`<div class="tr"><i>✓</i><span>${t}</span></div>`).join('')}</div>
<h2>${l.provs} <span class="ex">${l.real}</span></h2>
${prov(l,l.pName,`${l.cat1} · ${l.cityA}`,'5.0')}${prov(l,l.lang=='ar'?'فلاتر لتنقية المياه':'فلاتر لتنقية المياه',`${l.cat2} · ${l.cityB}`,'5.0')}</main>`,
provider:(l)=>`<main><div class="card"><div style="display:flex;gap:14px;align-items:center"><div class="av" style="width:72px;height:72px;font-size:28px">${[...l.pName][0]}</div><div><b style="font-size:19px;line-height:1.4;display:block">${l.pName}</b><span class="badge">✓ ${l.verified}</span> <small style="color:var(--m)">${l.pCity}</small><div style="color:var(--ok);font-weight:700;font-size:14px">● ${l.avail}</div></div></div>
<div style="display:flex;align-items:baseline;gap:8px;margin:14px 0"><span class="st" style="font-size:30px">★ 5.0</span><small style="color:var(--m)">${l.one} · ${l.done}</small></div>
<div class="btn">${l.chat}</div><div style="display:flex;gap:8px;margin-top:10px"><div class="btn2">${l.share}</div><div class="btn2">${l.save}</div></div></div>
<div class="card"><b>${l.pDesc}</b><div class="row" style="margin-top:12px"><span style="color:var(--m)">${l.pRange}</span></div><div class="row"><small style="color:var(--m)">${l.pRangeNote}</small></div></div>
<h2>${l.reviews} <span class="ex">${l.real}</span></h2><div class="card"><div style="display:flex;justify-content:space-between"><b>${l.rvName} <span class="badge">✓ ${l.verified}</span></b><span class="st">★★★★★</span></div><small style="color:var(--m)">${l.rvAgo}</small><p style="margin-top:8px">${l.rv}</p></div></main>`,
search:(l)=>`<main><div class="f" style="margin-bottom:8px;background:var(--s)">${l.cat1} · ${l.cityA}</div><div class="fl">${l.filters.map(c=>`<span class="chip">${c}</span>`).join('')}</div>
<h2 style="margin-top:4px">${l.resTitle} <span class="ex">${l.exampleBadge}</span></h2>
${prov(l,l.pName,`${l.cat1} · ${l.cityA}`,'5.0')}${prov(l,l.lang=='ar'?'مثال: فني كهرباء':'Example: electrician',`${l.cat1} · ${l.cityA}`,null)}
<div class="card" style="margin-top:12px"><b>${l.e3}</b><div class="btn" style="margin-top:12px">${l.e3b}</div></div></main>`,
empty:(l)=>`<main><div class="f" style="background:var(--s)">${l.lang=='ar'?'زززقق':'zzzqqq'} · ${l.cityA}</div>
<div class="card" style="text-align:center;padding:24px 16px"><div style="font-size:40px">🔎</div><h2 style="margin:8px 0">${l.emptyT}</h2><p style="color:var(--m)">${l.emptyP}</p></div>
<div class="card" style="padding:4px 16px">${[[l.e1,l.e1b],[l.e2,l.e2b],[l.e3,l.e3b]].map((s,i)=>`<div class="step" ${i==0?'style="border:0"':''}><span class="n">${i+1}</span><p>${s[0]}</p><a>${s[1]}</a></div>`).join('')}</div>
<div class="btn">${l.e3b}</div><a class="lnk">${l.browse}</a><div class="chips" style="margin-top:12px">${l.chips.map(c=>`<span class="chip">${c}</span>`).join('')}</div></main>`
};
const navOn={home:0,provider:1,search:1,empty:1};
function html(page,lang,th){const l=L[lang],T=THEMES[th];
 return `<!doctype html><html lang="${l.lang}" dir="${l.dir}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>mockup</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet"><style>${css(T,l)}</style></head><body>${head(l,th)}${pages[page](l)}${foot(l)}${nav(l,navOn[page])}</body></html>`}
function wcag(a,b){const f=h=>{const v=[1,3,5].map(i=>parseInt(h.slice(i,i+2),16)/255).map(c=>c<=.03928?c/12.92:((c+.055)/1.055)**2.4);return .2126*v[0]+.7152*v[1]+.0722*v[2]};const x=f(a),y=f(b);return ((Math.max(x,y)+.05)/(Math.min(x,y)+.05)).toFixed(1)}
(async()=>{
 const b=await chromium.launch();
 const shot=async(file,out,w=390)=>{const c=await b.newContext({viewport:{width:w,height:844},deviceScaleFactor:2});const p=await c.newPage();await p.goto('file://'+file);await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(400);await p.screenshot({path:out,fullPage:true});await c.close()};
 fs.mkdirSync(ROOT+'/html',{recursive:true});
 const out={};
 for(const lang of ['ar','en'])for(const page of Object.keys(pages)){
   const f=`${ROOT}/html/simple-${page}-${lang}-identity.html`;fs.writeFileSync(f,html(page,lang,'identity'));
   await shot(f,`${ROOT}/simple-${page}-${lang}-390.png`)}
 for(const th of Object.keys(THEMES)){const f=`${ROOT}/html/simple-home-ar-${th}.html`;fs.writeFileSync(f,html('home','ar',th));await shot(f,`${ROOT}/src/_home-${th}.png`)}
 for(const th of Object.keys(THEMES)){console.log(th,'text/bg',wcag(THEMES[th].text,THEMES[th].bg),'btn',wcag(THEMES[th].primaryFg,THEMES[th].primary),'muted/bg',wcag(THEMES[th].muted,THEMES[th].bg))}
 // لوحة الألوان
 const pal=`<!doctype html><meta charset=utf-8><body style="margin:0;background:#888;font-family:Cairo,sans-serif;direction:rtl"><div style="display:flex;gap:24px;padding:24px;width:max-content">${Object.keys(THEMES).map(th=>`<div><div style="color:#fff;font-weight:800;font-size:22px;text-align:center;margin-bottom:8px">${THEMES[th].n}</div><img src="_home-${th}.png" style="width:390px;display:block"></div>`).join('')}</div>`;
 fs.writeFileSync(ROOT+'/src/_pal.html',pal);
 { const c=await b.newContext({viewport:{width:1700,height:900},deviceScaleFactor:1});const p=await c.newPage();await p.goto('file://'+ROOT+'/src/_pal.html');await p.waitForTimeout(500);await p.screenshot({path:ROOT+'/palette-4-colors.png',fullPage:true});await c.close()}
 // مقارنة: يسار المقترح، يمين الحالي
 const cmp=[['home','home-390.png','simple-home-ar-390.png'],['provider','provider-390.png','simple-provider-ar-390.png'],['search','search-390.png','simple-search-ar-390.png'],['empty','empty-390.png','simple-empty-ar-390.png']];
 for(const [n,cur,prop] of cmp){
  const h=`<!doctype html><meta charset=utf-8><body style="margin:0;background:#777"><div style="display:flex;gap:20px;padding:20px;align-items:flex-start;width:max-content"><div><div style="color:#fff;font:800 20px sans-serif;margin-bottom:6px">Proposed / المقترح (المبسّط)</div><img src="../${prop}" style="width:390px;display:block;max-height:2000px;object-fit:cover;object-position:top"></div><div><div style="color:#fff;font:800 20px sans-serif;margin-bottom:6px">Current / الحالي</div><img src="../current/${cur}" style="width:390px;display:block;max-height:2000px;object-fit:cover;object-position:top"></div></div>`;
  fs.writeFileSync(`${ROOT}/src/_cmp-${n}.html`,h);
  const c=await b.newContext({viewport:{width:860,height:900},deviceScaleFactor:1});const p=await c.newPage();await p.goto('file://'+`${ROOT}/src/_cmp-${n}.html`);await p.waitForTimeout(500);await p.screenshot({path:`${ROOT}/compare-${n}.png`,fullPage:true});await c.close()}
 await b.close()})();
