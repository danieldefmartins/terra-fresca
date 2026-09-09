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
await call('Runtime.enable');
const errors=[];ws.addEventListener('message',e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text)});
const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.result.exceptionDetails)throw Error(JSON.stringify(r.result.exceptionDetails));return r.result.result.value;};
for(const [name,width,height] of [['desktop',1440,900],['mobile',390,844]]){
 await call('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:name==='mobile'});
 await call('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
 await call('Page.navigate',{url});
 for(let i=0;i<100;i++){if(await evaluate('window.__globe?.drawn'))break;await delay(150);}
 if(!await evaluate('window.__globe?.drawn'))errors.push(name+' Orange globe unavailable');
 await delay(1500);
 if(name==='mobile'){await evaluate(`lenis.scrollTo(Math.max(0,document.querySelector('.hero').offsetHeight-innerHeight),{immediate:true})`);await delay(300);}
 const coverage=await evaluate(`(()=>{const c=document.querySelector('#globeCv'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;let n=0;for(let i=3;i<d.length;i+=64)if(d[i]>20)n++;return n/(d.length/64)})()`);
 if(coverage<.05)errors.push(name+' globe canvas blank');
 for(const view of ['americas','rotated']){
  if(view==='rotated'){await evaluate("document.querySelector('#globeCv').focus()");for(let i=0;i<12;i++)await call('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39});await delay(500);}
  const shot=await call('Page.captureScreenshot',{format:'jpeg',quality:90});await writeFile(new URL(name+'-orange-glow-'+view+'.jpg',output),Buffer.from(shot.result.data,'base64'));
 }
}
await call('Emulation.setTouchEmulationEnabled',{enabled:true,maxTouchPoints:1});
await evaluate(`lenis.scrollTo(Math.max(0,document.querySelector('.hero').offsetHeight-innerHeight),{immediate:true})`);await delay(300);
const touchCenter=await evaluate(`(()=>{const r=document.querySelector('#globeTouch').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2}})()`);
const beforeTouch=await evaluate('({y:scrollY,tilt:window.__globe.tilt})');
await call('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...touchCenter,id:1}]});
for(let i=1;i<=8;i++){await call('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:touchCenter.x+5*i,y:touchCenter.y-12*i,id:1}]});await delay(35);}
await call('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await delay(200);
const afterTouch=await evaluate('({y:scrollY,tilt:window.__globe.tilt,stopped:lenis.isStopped})');
if(Math.abs(afterTouch.y-beforeTouch.y)>2||Math.abs(afterTouch.tilt-beforeTouch.tilt)<.2||afterTouch.stopped)errors.push('Globe touch did not exclusively rotate');
await call('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:12,y:180,id:2}]});
for(let i=1;i<=8;i++){await call('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:12,y:180-i*12,id:2}]});await delay(35);}
await call('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await delay(500);
if(await evaluate('scrollY')<afterTouch.y+30)errors.push('Scrolling outside the globe blocked');
console.log('Orange globe checks',errors);ws.close();browser.kill('SIGTERM');if(errors.length)process.exitCode=1;
