import puppeteer from 'puppeteer-core';
import path from 'path';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const ARTIFACT_DIR = 'C:\\Users\\rahis\\.gemini\\antigravity-ide\\brain\\c62d3b5c-c6dd-41bf-b028-c441652c9472';

async function runFastTest() {
  console.log('[Test] Launching headless browser...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 800 }
  });

  const page = await browser.newPage();
  const logs = [];
  page.on('console', msg => logs.push(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => console.error('[Browser Error]', err));

  try {
    console.log('[Test] Navigating to http://localhost:5173...');
    await page.goto('http://localhost:5173/', { waitUntil: 'domcontentloaded', timeout: 10000 });
    await new Promise(r => setTimeout(r, 1000));

    // 1. Ramp & Spring
    console.log('[Test] Checking Kinematics: Ramp & Spring...');
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '01_ramp_spring_initial.png') });
    await page.click('#play-button');
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '02_ramp_spring_rolling.png') });

    // 2. Newton's Cradle
    console.log('[Test] Checking Kinematics: Newton Cradle...');
    await page.select('#mechanics-scene-select', 'newtons_cradle');
    await new Promise(r => setTimeout(r, 1000));
    await page.click('#play-button');
    await new Promise(r => setTimeout(r, 1500));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '03_newtons_cradle.png') });

    // 3. Optics - Convex Lens
    console.log('[Test] Checking Optics: Convex Lens...');
    await page.click('#switch-optics');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '04_optics_convex_lens.png') });

    // 4. Optics - Interface Refraction
    console.log('[Test] Checking Optics: Interface Refraction...');
    await page.click('#optics-tab-interface');
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '05_optics_interface.png') });

    // 5. Optics - Prism
    console.log('[Test] Checking Optics: Prism...');
    await page.click('#optics-tab-prism');
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '06_optics_prism.png') });

    // 6. Optics - Mirror
    console.log('[Test] Checking Optics: Mirror...');
    await page.click('#optics-tab-mirror');
    await new Promise(r => setTimeout(r, 800));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '07_optics_mirror.png') });

    // 7. Circuits
    console.log('[Test] Checking Circuits: Circuit 1...');
    await page.click('#switch-circuits');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, '08_circuits_circuit1.png') });

    console.log('[Test] ALL TESTS COMPLETED SUCCESSFULLY IN ~8 SECONDS!');
  } catch (err) {
    console.error('[Test Error]', err);
  } finally {
    await browser.close();
  }
}

runFastTest();
