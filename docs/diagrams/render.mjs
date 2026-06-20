// Render every *.svg in this folder to a matching *.png using the chromium
// that Playwright already installs for the @taskflow/e2e package.
//   node docs/diagrams/render.mjs [scale=2]
import { createRequire } from 'node:module';
import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
// Resolve Playwright from the e2e workspace rather than this folder.
const require = createRequire(new URL('../../e2e/package.json', import.meta.url));
const pw = await import(pathToFileURL(require.resolve('@playwright/test')).href);
const chromium = pw.chromium ?? pw.default?.chromium;

const scale = Number(process.argv[2] ?? 2);
const svgs = readdirSync(here).filter((f) => f.endsWith('.svg'));
if (svgs.length === 0) {
  console.log('No .svg files found in', here);
  process.exit(0);
}

const browser = await chromium.launch();
for (const file of svgs) {
  const svg = readFileSync(join(here, file), 'utf8');
  const w = Number(svg.match(/width="(\d+)"/)[1]);
  const h = Number(svg.match(/height="(\d+)"/)[1]);
  const page = await browser.newPage({ deviceScaleFactor: scale });
  await page.setViewportSize({ width: w, height: h });
  await page.setContent(
    `<!doctype html><meta charset="utf8"><body style="margin:0">${svg}</body>`,
    { waitUntil: 'networkidle' },
  );
  const out = file.replace(/\.svg$/, '.png');
  await page.locator('svg').screenshot({ path: join(here, out) });
  await page.close();
  console.log(`✓ ${file} → ${out} (${w}×${h} @${scale}x)`);
}
await browser.close();
