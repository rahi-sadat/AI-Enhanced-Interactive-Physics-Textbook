import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const SCREENSHOT_DIR = 'C:\\Users\\rahis\\.gemini\\antigravity-ide\\brain\\27c9f832-932e-4bb9-96f7-f52922186ce7\\scratch';

async function runBrowserTests() {
  console.log('--- Starting Automated Browser Verification ---');

  if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
  }

  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 900 }
  });

  const page = await browser.newPage();

  const consoleLogs = [];
  const errors = [];

  page.on('console', msg => {
    const text = msg.text();
    consoleLogs.push({ type: msg.type(), text });
    if (msg.type() === 'error') {
      console.error('[Browser Error]', text);
    }
  });

  page.on('pageerror', err => {
    errors.push(err.toString());
    console.error('[Page Uncaught Error]', err.toString());
  });

  try {
    console.log('1. Navigating to http://localhost:5173 ...');
    await page.goto('http://localhost:5173', { waitUntil: 'networkidle2', timeout: 15000 });
    console.log('   Page loaded successfully.');

    // ----------------------------------------------------
    // TEST 1: Simple Pendulum (Kinematics RK4 Precision)
    // ----------------------------------------------------
    console.log('\n2. Testing Simple Pendulum (Kinematics) preset...');
    await page.waitForSelector('#btn-open-upload', { visible: true });
    await page.click('#btn-open-upload');

    await page.waitForSelector('.preset-pill[data-preset="pendulum_test1"]', { visible: true });
    await page.click('.preset-pill[data-preset="pendulum_test1"]');

    // Small delay to let preview register
    await new Promise(r => setTimeout(r, 600));

    await page.waitForSelector('#btn-generate-sim:not([disabled])', { visible: true });
    await page.click('#btn-generate-sim');

    console.log('   Clicked Generate Simulation, awaiting synthesis...');
    await page.waitForFunction(() => {
      const modal = document.getElementById('upload-modal');
      return modal && modal.style.display === 'none';
    }, { timeout: 20000 });

    // Wait for physics overlay canvas to mount
    await new Promise(r => setTimeout(r, 2000));

    const pendulumState = await page.evaluate(() => {
      const img = document.getElementById('diagram-image');
      const canvas = document.querySelector('#simulation-container canvas');
      const activeTab = document.querySelector('.domain-btn.active')?.id;
      const mechanicsVisible = document.getElementById('mechanics-controls')?.style.display !== 'none';
      const gravityVal = document.getElementById('gravity-slider')?.value;
      const pendControlVisible = document.getElementById('pendulum-controls-group')?.style.display !== 'none';
      const pendLength = document.getElementById('pendulum-length-input')?.value;

      return {
        imageSrc: img?.src,
        canvasClass: canvas?.className,
        canvasWidth: canvas?.width,
        canvasHeight: canvas?.height,
        activeTab,
        mechanicsVisible,
        gravityVal,
        pendControlVisible,
        pendLength,
      };
    });

    console.log('   Pendulum State:', JSON.stringify(pendulumState, null, 2));

    const pendulumScreenshotPath = path.join(SCREENSHOT_DIR, 'test_pendulum_overlay.png');
    await page.screenshot({ path: pendulumScreenshotPath, fullPage: false });
    console.log('   Saved pendulum screenshot to:', pendulumScreenshotPath);

    // Test pointer drag on bob to new angle
    const canvasRect = await page.$eval('#simulation-container canvas', el => {
      const r = el.getBoundingClientRect();
      return { left: r.left, top: r.top, width: r.width, height: r.height };
    });
    // Drag bob towards center right
    await page.mouse.move(canvasRect.left + canvasRect.width * 0.35, canvasRect.top + canvasRect.height * 0.7);
    await page.mouse.down();
    await page.mouse.move(canvasRect.left + canvasRect.width * 0.55, canvasRect.top + canvasRect.height * 0.7, { steps: 5 });
    await new Promise(r => setTimeout(r, 300));
    const dragScreenshotPath = path.join(SCREENSHOT_DIR, 'test_pendulum_dragged.png');
    await page.screenshot({ path: dragScreenshotPath, fullPage: false });
    console.log('   Saved dragged pendulum screenshot to:', dragScreenshotPath);
    await page.mouse.up();

    // Play simulation and capture swinging state
    await page.click('#play-button');
    await new Promise(r => setTimeout(r, 800));
    const swingScreenshotPath = path.join(SCREENSHOT_DIR, 'test_pendulum_swinging.png');
    await page.screenshot({ path: swingScreenshotPath, fullPage: false });
    console.log('   Saved swinging pendulum screenshot to:', swingScreenshotPath);
    await page.click('#pause-button');

    // ----------------------------------------------------
    // TEST 2: Concave Mirror (Optics Figure 8.23)
    // ----------------------------------------------------
    console.log('\n3. Testing Concave Mirror (Optics) preset...');
    await page.click('#btn-open-upload');

    await page.waitForSelector('.preset-pill[data-preset="mirror_cff"]', { visible: true });
    await page.click('.preset-pill[data-preset="mirror_cff"]');

    await new Promise(r => setTimeout(r, 600));

    await page.waitForSelector('#btn-generate-sim:not([disabled])', { visible: true });
    await page.click('#btn-generate-sim');

    console.log('   Clicked Generate Simulation for Mirror, awaiting synthesis...');
    await page.waitForFunction(() => {
      const modal = document.getElementById('upload-modal');
      return modal && modal.style.display === 'none';
    }, { timeout: 20000 });

    // Wait for p5 optics renderer to mount
    await new Promise(r => setTimeout(r, 2000));

    const mirrorState = await page.evaluate(() => {
      const img = document.getElementById('diagram-image');
      const canvas = document.querySelector('#simulation-container canvas');
      const activeTab = document.querySelector('.domain-btn.active')?.id;
      const opticsVisible = document.getElementById('optics-controls')?.style.display !== 'none';
      const scenarioSelect = document.getElementById('optics-scene-select')?.value;
      const mirrorTabActive = document.getElementById('optics-tab-mirror')?.classList.contains('active');
      const mirrorTypeGroupVisible = document.getElementById('mirror-type-group')?.style.display !== 'none';
      const mirrorType = document.getElementById('mirror-type-select')?.value;
      const hudText = document.getElementById('optics-hud')?.innerText;

      return {
        imageSrc: img?.src,
        canvasWidth: canvas?.width,
        canvasHeight: canvas?.height,
        activeTab,
        opticsVisible,
        scenarioSelect,
        mirrorTabActive,
        mirrorTypeGroupVisible,
        mirrorType,
        hudText: hudText?.slice(0, 150),
      };
    });

    console.log('   Mirror State:', JSON.stringify(mirrorState, null, 2));

    const mirrorScreenshotPath = path.join(SCREENSHOT_DIR, 'test_mirror_overlay.png');
    await page.screenshot({ path: mirrorScreenshotPath, fullPage: false });
    console.log('   Saved mirror screenshot to:', mirrorScreenshotPath);

    console.log('\n--- Automated Browser Verification Finished ---');
    console.log(`Total Errors Logged: ${errors.length}`);
    if (errors.length > 0) {
      console.error('Errors encountered during test:', errors);
    }

  } catch (err) {
    console.error('Fatal test execution failure:', err);
  } finally {
    await browser.close();
  }
}

runBrowserTests();
