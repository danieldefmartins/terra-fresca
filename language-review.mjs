#!/usr/bin/env node
/** Check journey navigation, page assets, overflow and runtime errors in Chrome.
 * Run: node motion-review.mjs [URL]. Captures intermediate truck poses.
 */
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { platform } from 'node:os';

const url = process.argv[2] || 'http://localhost:3457';
const chrome = process.env.CHROME_PATH || (platform() === 'darwin'
  ? '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
  : 'google-chrome');
const port = 9300 + process.pid % 300;
const output = new URL('./.visual-checkpoints/', import.meta.url);
await mkdir(output, { recursive: true });

const browser = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--use-angle=metal', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/brazil-fresh-visuals-${process.pid}`, 'about:blank'
], { stdio: ['ignore','ignore','pipe'] });

browser.stderr.resume();
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
async function targets() {
  for (let i = 0; i < 150; i++) {
    try { return await (await fetch(`http://127.0.0.1:${port}/json`)).json(); }
    catch { await delay(100); }
  }
  throw new Error('Chrome debugging endpoint did not start');
}

const targetList = await targets();
const { webSocketDebuggerUrl } = targetList.find(target => target.type === 'page' && target.url === 'about:blank')
  || targetList.find(target => target.type === 'page')
  || targetList[0];
const ws = new WebSocket(webSocketDebuggerUrl);
await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
let sequence = 0;
const pending = new Map();
ws.onmessage = event => {
  const message = JSON.parse(event.data);
  if (message.id && pending.has(message.id)) {
    pending.get(message.id)(message);
    pending.delete(message.id);
  }
};
const call = (method, params = {}) => new Promise(resolve => {
  const id = ++sequence;
  pending.set(id, resolve);
  ws.send(JSON.stringify({ id, method, params }));
});

await call('Page.enable');

const failures=[];
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value;};

async function until(expression,timeout=55000){const start=Date.now();while(Date.now()-start<timeout){try{if(await evaluate(expression))return;}catch{}await delay(200)}throw Error('Timed out: '+expression)}
try {
 await call('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await call('Page.navigate',{url});await until(`!!document.querySelector('.language-menu')`);
 await evaluate(`document.querySelector('.language-menu').open=true`);
 await until(`!!document.querySelector('.gt_selector')`);
 const options=await evaluate(`[...document.querySelector('.gt_selector').options].map(o=>o.value)`);
 if(options.length!==10)failures.push('Language count');
 for(const lang of ['es','pt','zh-CN','it','fr','ar','de','ja','ko','en']){
  await evaluate(`(()=>{const s=document.querySelector('.gt_selector');s.value='en|${lang}';s.dispatchEvent(new Event('change',{bubbles:true}))})()`);
  await until(`document.documentElement.lang==='${lang}'&&!document.querySelector('.language-menu').hasAttribute('aria-busy')`);
  if(lang!=='en')await until(`document.querySelector('h1').innerText!=='FROM BRAZILIAN SOIL TO TABLES WORLDWIDE'`);
  await delay(800);
  const state=await evaluate(`({lang:document.documentElement.lang,dir:document.documentElement.dir,h1:document.querySelector('h1').innerText,overflow:document.documentElement.scrollWidth>innerWidth+2})`);
  console.log(state);
  if(state.overflow)failures.push(lang+' overflow');
 }
 await evaluate(`(()=>{const s=document.querySelector('.gt_selector');s.value='en|ar';s.dispatchEvent(new Event('change',{bubbles:true}))})()`);
 await until(`document.documentElement.lang==='ar'`);
 await call('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});
 await call('Page.navigate',{url:new URL('/produce/yuca/',url).href});
 await until(`location.pathname==='/produce/yuca/'&&document.documentElement.dir==='rtl'&&document.documentElement.lang==='ar'&&!document.querySelector('.language-menu').hasAttribute('aria-busy')`);
 await delay(800);
 console.log(await evaluate(`({product:document.querySelector('h1').innerText,dir:document.documentElement.dir,overflow:document.documentElement.scrollWidth>innerWidth+2})`));
 if(await evaluate(`document.documentElement.scrollWidth>innerWidth+2`))failures.push('Arabic product mobile overflow');
 let shot=await call('Page.captureScreenshot',{format:'jpeg',quality:85});await writeFile(new URL('language-arabic-product.jpg',output),Buffer.from(shot.result.data,'base64'));
 await call('Page.navigate',{url});await until(`location.pathname==='/'&&document.documentElement.dir==='rtl'&&document.documentElement.lang==='ar'&&!document.querySelector('.language-menu').hasAttribute('aria-busy')`);
 await delay(800);
 await evaluate(`document.querySelector('.language-menu').open=true`);
 shot=await call('Page.captureScreenshot',{format:'jpeg',quality:85});await writeFile(new URL('language-arabic-home.jpg',output),Buffer.from(shot.result.data,'base64'));
 if(await evaluate(`document.documentElement.scrollWidth>innerWidth+2`))failures.push('Arabic home mobile overflow');
 await evaluate(`localStorage.clear()`);
 await call('Network.enable');await call('Network.setBlockedURLs',{urls:['*cdn.gtranslate.net*']});
 await call('Page.navigate',{url});await until(`!!document.querySelector('.language-menu')`);
 await evaluate(`document.querySelector('.language-menu').open=true`);
 await until(`document.querySelector('.language-retry')?.hidden===false`);
 if(await evaluate(`document.querySelector('h1').innerText`)!=='FROM BRAZILIAN SOIL TO TABLES WORLDWIDE')failures.push('Provider failure changed English');
 await call('Network.setBlockedURLs',{urls:[]});await evaluate(`document.querySelector('.language-retry').click()`);
 await until(`!!document.querySelector('.gt_selector')`);
 console.log('Blocked provider recovery passed');
} catch(error) {failures.push(error.message);console.log(await evaluate(`({text:document.querySelector('.language-status')?.textContent,ready:window.__GT?.translator?.libReady,error:window.__GT?.translator?.errorCode,lang:document.documentElement.lang})`));}
console.log(JSON.stringify({failures},null,2));
ws.close();browser.kill('SIGTERM');if(failures.length)process.exitCode=1;
