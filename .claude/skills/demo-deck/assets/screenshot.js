#!/usr/bin/env node
// Screenshot a URL (or local file://) to a PNG, for embedding in a deck slide.
// Headless, no MCP needed -- use this for anything reachable without a login.
// For a page behind an authenticated session (a live Grafana, a private
// dashboard), use the claude-in-chrome MCP tools instead: they drive the
// user's real logged-in browser. See SKILL.md "Web screenshots".
//
// Usage:
//   node screenshot.js <url> <out.png> [--width 1600] [--height 1000]
//                                      [--full] [--wait <cssSelector>]
//                                      [--delay <ms>] [--dark]
//
//   --full   capture the entire scrollable page, not just the viewport
//   --wait   block until this selector appears (for JS-rendered pages)
//   --delay  extra settle time in ms after load (default 400)
//   --dark   ask the page for its dark colour scheme, so it sits better on a
//            dark deck (only works if the site actually supports it)
const puppeteer = require('/Users/cns/.nvm/versions/node/v22.19.0/lib/node_modules/@mermaid-js/mermaid-cli/node_modules/puppeteer');

function arg(name, dflt) {
  const i = process.argv.indexOf(name);
  return i > -1 ? process.argv[i + 1] : dflt;
}
const has = (name) => process.argv.includes(name);

const [url, out] = process.argv.slice(2).filter((a) => !a.startsWith('--') );
if (!url || !out) {
  console.error('usage: node screenshot.js <url> <out.png> [--width N] [--height N] [--full] [--wait sel] [--delay ms] [--dark]');
  process.exit(1);
}

(async () => {
  const b = await puppeteer.launch({
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: 'new',
    args: ['--no-sandbox'],
  });
  const pg = await b.newPage();
  await pg.setViewport({
    width: parseInt(arg('--width', '1600'), 10),
    height: parseInt(arg('--height', '1000'), 10),
    deviceScaleFactor: 2, // retina -- keeps text crisp when scaled on a 1920x1080 slide
  });
  if (has('--dark')) {
    await pg.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'dark' }]);
  }
  await pg.goto(url, { waitUntil: 'networkidle0', timeout: 60000 });
  const waitSel = arg('--wait', null);
  if (waitSel) await pg.waitForSelector(waitSel, { timeout: 30000 });
  await new Promise((r) => setTimeout(r, parseInt(arg('--delay', '400'), 10)));
  await pg.screenshot({ path: out, fullPage: has('--full') });
  await b.close();
  console.log('captured', url, '->', out);
})().catch((e) => { console.error('SCREENSHOT FAIL', e.message); process.exit(1); });
