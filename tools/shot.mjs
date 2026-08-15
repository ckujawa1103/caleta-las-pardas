import { chromium } from 'playwright';
const page1 = process.argv[2] || 'index.html';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
for (const [name, w, h] of [['desktop',1440,1000],['phone',390,844]]) {
  const ctx = await b.newContext({ viewport:{width:w,height:h}, deviceScaleFactor: name==='phone'?2:1 });
  const p = await ctx.newPage();
  const errs=[];
  p.on('pageerror', e=>errs.push('JS: '+e.message));
  p.on('console', m=>{ if(m.type()==='error') errs.push('CONSOLE: '+m.text()); });
  await p.goto('http://localhost:8899/' + page1, { waitUntil:'networkidle' });
  await p.waitForTimeout(600);
  await p.screenshot({ path:`/tmp/shot-${name}-top.png` });
  await p.screenshot({ path:`/tmp/shot-${name}-full.png`, fullPage:true });
  if(errs.length) console.log(name, 'ERRORS:', errs.join(' | '));
  const m = await p.evaluate(()=>({ sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth }));
  console.log(name, 'scrollWidth', m.sw, 'clientWidth', m.cw, m.sw>m.cw?'*** H-OVERFLOW':'ok');
  await ctx.close();
}
await b.close();
