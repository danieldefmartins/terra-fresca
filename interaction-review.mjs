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
const links=[];
for(const [name,width,height] of [['desktop',1440,900],['mobile',390,844]]){
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:name==='mobile'});
 await call('Page.navigate',{url});await delay(1500);
 if(name==='desktop')links.push(...await evaluate(`Promise.all([...document.querySelectorAll('a.produce-card')].map(async a=>{const r=await fetch(a.href);return {href:a.getAttribute('href'),ok:r.ok&&/<h1/.test(await r.text())}}))`));
 await evaluate(`lenis.scrollTo(document.querySelector('#producePrelude').offsetTop+document.querySelector('.produce-heading').offsetHeight,{immediate:true})`);
 await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:width-2,y:height-2});await delay(5700);
 const auto=await evaluate(`document.querySelector('.produce-track').scrollLeft`);if(auto<width*.8)failures.push(name+' autoplay');
 const initialY=await evaluate('scrollY');
 const arrow=await evaluate(`(()=>{const r=document.querySelector('[data-produce-step="1"]').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()`);
 await call('Input.dispatchMouseEvent',{type:'mousePressed',...arrow,button:'left',buttons:1,clickCount:1});await call('Input.dispatchMouseEvent',{type:'mouseReleased',...arrow,button:'left',buttons:0,clickCount:1});await delay(900);
 if(Math.abs(await evaluate('scrollY')-initialY)>3)failures.push(name+' arrows moved page');
 const x=await evaluate(`document.querySelector('.produce-track').scrollLeft`);
 await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:width-2,y:height-2});await delay(5300);
 if(Math.abs(await evaluate(`document.querySelector('.produce-track').scrollLeft`)-x)>4)failures.push(name+' automation did not stop after arrow');
 if(await evaluate(`document.querySelectorAll('.produce-navigation button').length!==2||!!document.querySelector('#producePause,#produceCount')`))failures.push(name+' extra controls');
 await call('Input.dispatchMouseEvent',{type:'mouseWheel',x:width/2,y:300,deltaY:340,deltaX:0});await delay(900);
 if(await evaluate('scrollY')<initialY+150||Math.abs(await evaluate(`document.querySelector('.produce-track').scrollLeft`)-x)>4)failures.push(name+' vertical scroll changed carousel');
 await evaluate(`document.querySelector('.produce-card').focus()`);await delay(500);
 const shot=await call('Page.captureScreenshot',{format:'jpeg',quality:85});await writeFile(new URL(name+'-produce-carousel.jpg',output),Buffer.from(shot.result.data,'base64'));
 await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await delay(900);
 if(await evaluate('location.pathname')!=='/produce/mango/')failures.push(name+' detail navigation');
}
if(links.length!==17||new Set(links.map(l=>l.href)).size!==17||links.some(l=>!l.ok))failures.push('Produce destinations');
for(const path of ['/produce/potato/table-potato/','/produce/onion/','/produce/yuca/']){
 await call('Page.navigate',{url:new URL(path,url).href});await delay(900);
 const page=await evaluate(`({headings:[...document.querySelectorAll('h2')].map(h=>h.textContent),broken:[...document.images].some(i=>i.complete&&!i.naturalWidth),overflow:document.documentElement.scrollWidth>innerWidth+1})`);
 for(const h of ['Varieties','Availability through the year','Where it grows','Organic','Volume and packing','Research sources'])if(!page.headings.includes(h))failures.push(path+' missing '+h);
 if(page.broken||page.overflow)failures.push(path+' page layout/image');
}
await call('Network.enable');await call('Network.setBlockedURLs',{urls:['*terra-fleet.glb*']});
await call('Page.navigate',{url});await delay(1800);
await evaluate(`(()=>{const st=ScrollTrigger.getAll().find(s=>s.trigger?.id==='journeyFilm'&&s.animation?.duration()>10);lenis.scrollTo(st.start+100,{immediate:true})})()`);
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__fleet3d?.error)'))break;await delay(150);}
const fallback=await evaluate(`Boolean(window.__fleet3d?.error)&&!document.querySelector('#journeyFilm').classList.contains('fleet-active')&&getComputedStyle(document.querySelector('#filmSidePayload')).visibility==='visible'`);if(!fallback)failures.push('Model fallback');
console.log(JSON.stringify({produceLinks:links.length,fallback,failures},null,2));
ws.close();browser.kill('SIGTERM');if(failures.length)process.exitCode=1;
