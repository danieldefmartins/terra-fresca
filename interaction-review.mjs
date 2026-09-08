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
await call('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
await call('Page.navigate',{url});await delay(2000);
const links=await evaluate(`Promise.all([...document.querySelectorAll('a.produce-card')].map(async a=>{const r=await fetch(a.href);return {href:a.getAttribute('href'),ok:r.ok&&/<h1/.test(await r.text())}}))`);
if(links.length!==14||new Set(links.map(l=>l.href)).size!==14||links.some(l=>!l.ok))failures.push('Produce destinations');
const globe=await evaluate(`getComputedStyle(document.querySelector('#globeCv')).visibility==='visible'&&!document.querySelector('.hero .fleet-canvas')`);if(!globe)failures.push('Hero globe');
await evaluate(`document.querySelectorAll('a.produce-card')[13].focus()`);await delay(650);
const focused=await evaluate(`(()=>{const a=document.activeElement,r=a.getBoundingClientRect();return {href:a.getAttribute('href'),left:r.left,top:r.top}})()`);
if(focused.href!=='/produce/banana/'||Math.abs(focused.left)>30||Math.abs(focused.top)>30)failures.push('Keyboard positioning: '+JSON.stringify(focused));
await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await delay(1000);
if(await evaluate(`location.pathname`)!=='/produce/banana/')failures.push('Banana keyboard navigation');
await call('Page.navigate',{url});await delay(1500);await evaluate(`document.querySelector('a.produce-card').focus()`);await delay(600);
console.log('Pointer target',await evaluate(`({href:document.elementFromPoint(900,500)?.closest('a')?.getAttribute('href'),active:document.activeElement?.getAttribute('href'),x:document.querySelector('a.produce-card').getBoundingClientRect().left,y:scrollY})`));
await call('Input.dispatchMouseEvent',{type:'mouseMoved',x:900,y:500});await delay(100);await call('Input.dispatchMouseEvent',{type:'mousePressed',x:900,y:500,button:'left',buttons:1,clickCount:1});await delay(100);await call('Input.dispatchMouseEvent',{type:'mouseReleased',x:900,y:500,button:'left',buttons:0,clickCount:1});await delay(1000);
if(await evaluate(`location.pathname`)!=='/produce/mango/')failures.push('Mango pointer navigation: '+await evaluate('location.pathname'));
for(const [name,width,height] of [['desktop',1440,900],['mobile',390,844]]){
  await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:name==='mobile'});
  await call('Page.navigate',{url});await delay(1700);
  await evaluate(`lenis.scrollTo(document.querySelector('#producePrelude'),{immediate:true})`);await delay(600);
  await evaluate(`document.querySelector('[data-produce-step="1"]').click()`);await delay(1400);
  const geometry=await evaluate(`(()=>{const card=document.querySelector('.produce-card'),button=card.querySelector('.produce-details'),r=button.getBoundingClientRect(),nav=document.querySelector('.produce-navigation').getBoundingClientRect();return {left:card.getBoundingClientRect().left,height:r.height,weight:getComputedStyle(button).fontWeight,clear:r.bottom<nav.top}})()`);
  if(Math.abs(geometry.left)>30||geometry.height<48||Number(geometry.weight)<700||!geometry.clear)failures.push(name+' produce controls: '+JSON.stringify(geometry));
  const shot=await call('Page.captureScreenshot',{format:'jpeg',quality:85});await writeFile(new URL(name+'-produce-controls.jpg',output),Buffer.from(shot.result.data,'base64'));
  await evaluate(`document.querySelector('#produceContinue').click()`);await delay(600);
  if(await evaluate(`Math.abs(document.querySelector('#journeyFilm').getBoundingClientRect().top)>5||document.activeElement!==document.querySelector('#journeyFilm h2')`))failures.push(name+' continue navigation');
}
await call('Network.enable');await call('Network.setBlockedURLs',{urls:['*terra-fleet.glb*']});
await call('Page.navigate',{url});await delay(1800);
await evaluate(`(()=>{const st=ScrollTrigger.getAll().find(s=>s.trigger?.id==='journeyFilm'&&s.animation?.duration()>10);lenis.scrollTo(st.start+100,{immediate:true})})()`);
for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__fleet3d?.error)'))break;await delay(150);}
const fallback=await evaluate(`Boolean(window.__fleet3d?.error)&&!document.querySelector('#journeyFilm').classList.contains('fleet-active')&&getComputedStyle(document.querySelector('#filmSidePayload')).visibility==='visible'`);if(!fallback)failures.push('Model fallback');
console.log(JSON.stringify({produceLinks:links.length,heroGlobe:globe,keyboardFocus:focused,fallback,failures},null,2));
ws.close();browser.kill('SIGTERM');if(failures.length)process.exitCode=1;
