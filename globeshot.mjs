#!/usr/bin/env node
/* Drive the globe: drag it by (dx,dy) steps and capture each pose. */
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
const url = process.env.URL || 'http://localhost:3457/index.html';
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const port = 9600 + process.pid % 80;
const out = new URL('./.sweep/', import.meta.url);
await mkdir(out, { recursive: true });
const browser = spawn(chrome, ['--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/bf-globe-${process.pid}`, 'about:blank'], { stdio: 'ignore' });
const delay = ms => new Promise(r => setTimeout(r, ms));
let list;
for (let i = 0; i < 40; i++) { try { list = await (await fetch(`http://127.0.0.1:${port}/json`)).json(); break; } catch { await delay(100); } }
const ws = new WebSocket(list.find(t => t.type === 'page').webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0; const pending = new Map();
ws.onmessage = e => { const m = JSON.parse(e.data); if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); } };
const call = (m, p = {}) => new Promise(res => { const id = ++seq; pending.set(id, res); ws.send(JSON.stringify({ id, method: m, params: p })); });
await call('Page.enable');
await call('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, screenWidth: 1440, screenHeight: 900, deviceScaleFactor: 1, mobile: false });
await call('Page.navigate', { url }); await delay(2200);
// poses: [label, totalDx, totalDy]
const poses = JSON.parse(process.argv[2] || '[["rest",0,0],["spin",300,0],["up",0,-220],["down",0,240],["both",260,-180]]');
for (const [label, tdx, tdy] of poses) {
  // reset rotation state, then drive the drag handlers directly
  await call('Runtime.evaluate', { expression: `scrollTo(0,0)` });
  await delay(120);
  const cx = 1040, cy = 520, steps = 14;
  await call('Input.dispatchMouseEvent', { type: 'mousePressed', x: cx, y: cy, button: 'left', clickCount: 1 });
  for (let i = 1; i <= steps; i++) {
    await call('Input.dispatchMouseEvent', { type: 'mouseMoved', x: cx + tdx * i / steps, y: cy + tdy * i / steps, button: 'left' });
    await delay(12);
  }
  await call('Input.dispatchMouseEvent', { type: 'mouseReleased', x: cx + tdx, y: cy + tdy, button: 'left', clickCount: 1 });
  await delay(900);
  const shot = await call('Page.captureScreenshot', { format: 'jpeg', quality: 88 });
  await writeFile(new URL(`globe-${label}.jpg`, out), Buffer.from(shot.result.data, 'base64'));
  // undo so the next pose starts from a comparable place
  await call('Runtime.evaluate', { expression: `location.reload()` });
  await delay(2200);
}
ws.close(); browser.kill('SIGTERM');
console.log('globe poses captured');
