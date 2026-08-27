#!/usr/bin/env node
/* Fine-grained scroll sweep of one scene.
   Usage: node sweep.mjs <scene> <from> <to> <steps> [viewport] */
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';

const [scene = 'journeyFilm', from = '0.3', to = '0.5', steps = '12', vpName = 'desktop'] = process.argv.slice(2);
const url = process.env.URL || 'http://localhost:3457/index.html';
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const port = 9700 + process.pid % 200;
const out = new URL('./.sweep/', import.meta.url);
await mkdir(out, { recursive: true });

const browser = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/bf-sweep-${process.pid}`, 'about:blank'], { stdio: 'ignore' });
const delay = ms => new Promise(r => setTimeout(r, ms));
let list;
for (let i = 0; i < 40; i++) { try { list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await delay(100); } }
const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const call = (method, params = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method, params })); });

await call('Page.enable');
const vp = vpName === 'mobile' ? { width: 390, height: 844 } : { width: 1440, height: 900 };
await call('Emulation.setDeviceMetricsOverride', { ...vp, screenWidth: vp.width, screenHeight: vp.height, deviceScaleFactor: 1, mobile: vpName === 'mobile' });
await call('Page.navigate', { url });
await delay(2000);
await call('Runtime.evaluate', { expression: `document.querySelector('#producePrelude').style.height='${vp.height * 16.2}px';document.querySelector('#journeyFilm').style.height='${vp.height * (vpName === 'mobile' ? 12.5 : 14)}px';ScrollTrigger.refresh()` });
await delay(300);
const r = await call('Runtime.evaluate', { expression: `(()=>{const el=document.querySelector('#${scene}');return {top:el.offsetTop,height:el.offsetHeight}})()`, returnByValue: true });
const { top, height } = r.result.result.value;
const errs = await call('Runtime.evaluate', { expression: `window.__err||''`, returnByValue: true });
if (errs.result.result.value) console.log('PAGE ERROR:', errs.result.result.value);
const n = parseInt(steps, 10);
for (let i = 0; i < n; i++) {
  const f = parseFloat(from) + (parseFloat(to) - parseFloat(from)) * (i / (n - 1));
  const y = Math.round(top + height * f - vp.height / 2);
  await call('Runtime.evaluate', { expression: `scrollTo(0,${y})` });
  await delay(1500);
  const shot = await call('Page.captureScreenshot', { format: 'jpeg', quality: 84 });
  await writeFile(new URL(`${vpName}-${f.toFixed(4)}.jpg`, out), Buffer.from(shot.result.data, 'base64'));
}
ws.close(); browser.kill('SIGTERM');
console.log(`swept ${scene} ${from}->${to} (${n}) ${vpName}`);
