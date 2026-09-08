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
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
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
await call('Runtime.enable');
const errors=[];
ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text)});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value;};
for(const [name,width,height,reduced] of [['desktop',1440,900,false],['mobile',390,844,false],['reduced',1440,900,true]]){
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:name==='mobile'});
 await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:reduced?'reduce':'no-preference'}]});
 await call('Page.navigate',{url});await delay(2200);
 const state=await evaluate(`({overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src),chapters:document.querySelectorAll('.journey-chapters button').length})`);
 if(state.overflow||state.brokenImages.length||state.chapters!==5)errors.push(name+': '+JSON.stringify(state));
 console.log(name,JSON.stringify(state));
 for(const index of [4,0,2,3,1]){
  await evaluate(`document.querySelectorAll('.journey-chapters button')[${index}].click()`);await delay(1800);
  const current=await evaluate(`[...document.querySelectorAll('.journey-chapters button')].findIndex(b=>b.getAttribute('aria-current')==='step')`);
  if(current!==index)errors.push(name+': expected chapter '+index+', got '+current);
 }
 if(name==='desktop')for(const time of [3.88,4.0,4.16,4.3]){
  await evaluate(`(()=>{const st=ScrollTrigger.getAll().find(s=>s.trigger?.id==='journeyFilm'&&s.animation?.duration()>10);lenis.scrollTo(st.start+(st.end-st.start)*${time}/st.animation.duration(),{immediate:true})})()`);await delay(550);
  const shot=await call('Page.captureScreenshot',{format:'jpeg',quality:90});await writeFile(new URL('turn-'+time+'.jpg',output),Buffer.from(shot.result.data,'base64'));
 }
}
console.log('Failures:',JSON.stringify(errors));ws.close();browser.kill('SIGTERM');if(errors.length)process.exitCode=1;
