#!/usr/bin/env node
/* Evaluate an expression at a given scroll fraction of a scene. */
import { spawn } from 'node:child_process';
const [scene = 'journeyFilm', frac = '0.42', expr = '1', vpName = 'desktop'] = process.argv.slice(2);
const url = process.env.URL || 'http://localhost:3457/index.html';
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const port = 9900 + process.pid % 90;
const browser = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/bf-probe-${process.pid}`, 'about:blank'], { stdio: 'ignore' });
const delay = ms => new Promise(r => setTimeout(r, ms));
let list;
for (let i = 0; i < 40; i++) { try { list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await delay(100); } }
const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const call = (m, p = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method: m, params: p })); });
await call('Page.enable'); await call('Runtime.enable');
const errors = [];
ws.addEventListener('message', e => { const m = JSON.parse(e.data);
  if (m.method === 'Runtime.exceptionThrown') errors.push(m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text); });
const vp = vpName === 'mobile' ? { width: 390, height: 844 } : { width: 1440, height: 900 };
await call('Emulation.setDeviceMetricsOverride', { ...vp, screenWidth: vp.width, screenHeight: vp.height, deviceScaleFactor: 1, mobile: vpName === 'mobile' });
await call('Page.navigate', { url }); await delay(2000);
await call('Runtime.evaluate', { expression: `document.querySelector('#producePrelude').style.height='${vp.height * 10}px';document.querySelector('#journeyFilm').style.height='${vp.height * (vpName === 'mobile' ? 12.5 : 14)}px';ScrollTrigger.refresh()` });
await delay(300);
const r = await call('Runtime.evaluate', { expression: `(()=>{const el=document.querySelector('#${scene}');return {top:el.offsetTop,height:el.offsetHeight}})()`, returnByValue: true });
const { top, height } = r.result.result.value;
await call('Runtime.evaluate', { expression: `scrollTo(0,${Math.round(top + height * parseFloat(frac) - vp.height / 2)})` });
await delay(400);
const out = await call('Runtime.evaluate', { expression: `JSON.stringify(${expr})`, returnByValue: true });
console.log(out.result.result.value ?? out.result.result.description ?? JSON.stringify(out.result));
if (errors.length) console.log('ERRORS:', errors.slice(0, 5).join(' | '));
ws.close(); browser.kill('SIGTERM');
