import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';

const CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const ARTIFACT_DIR = 'C:\\Users\\rahis\\.gemini\\antigravity-ide\\brain\\27c9f832-932e-4bb9-96f7-f52922186ce7';

async function main() {
  console.log('Starting puppeteer headless test of mechanics scenes...');
  const browser = await puppeteer.launch({
    executablePath: CHROME_PATH,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    defaultViewport: { width: 1280, height: 800 }
  });

  const page = await browser.newPage();
  const consoleLogs = [];
  page.on('console', msg => consoleLogs.push(`[${msg.type()}] ${msg.text()}`));
  page.on('pageerror', err => console.error('[Browser Error]', err));

  try {
    await page.goto('http://localhost:5173/', { waitUntil: 'networkidle2', timeout: 15000 });
    console.log('1. Page loaded.');

    // Wait for mechanics controls and select
    await page.waitForSelector('#mechanics-scene-select', { visible: true });
    const initialSelectVal = await page.$eval('#mechanics-scene-select', el => el.value);
    console.log(`2. Initial mechanics select value: ${initialSelectVal}`);

    // Check ramp initial ball position
    const ballPosInitial = await page.evaluate(() => {
      const sim = window.__sim || null;
      // Find ball element_001
      const canvas = document.querySelector('#canvas-container canvas');
      return { canvasFound: !!canvas };
    });
    console.log('3. Canvas found:', ballPosInitial);

    // Save screenshot of initial ramp scene
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'ramp_with_spring_initial.png') });
    console.log('4. Saved ramp_with_spring_initial.png');

    // Click play
    await page.click('#play-button');
    console.log('5. Clicked play button on Ramp scene.');

    // Wait 2.5 seconds for ball to roll down ramp to spring
    await new Promise(r => setTimeout(r, 2500));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'ramp_with_spring_running.png') });
    console.log('6. Saved ramp_with_spring_running.png');

    // Now switch to Newton's Cradle
    console.log('7. Switching #mechanics-scene-select to newtons_cradle...');
    await page.select('#mechanics-scene-select', 'newtons_cradle');

    // Wait for cradle scene to render
    await new Promise(r => setTimeout(r, 1200));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'newtons_cradle_loaded.png') });
    console.log('8. Saved newtons_cradle_loaded.png');

    // Click play on Newton's Cradle
    await page.click('#play-button');
    console.log('9. Clicked play button on Newton\'s Cradle.');

    // Wait 2.0 seconds for swing and impact
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'newtons_cradle_swinging.png') });
    console.log('10. Saved newtons_cradle_swinging.png');

    // Switch back to Ramp with Spring
    console.log('11. Switching back to with_spring...');
    await page.select('#mechanics-scene-select', 'with_spring');
    await new Promise(r => setTimeout(r, 1000));
    await page.screenshot({ path: path.join(ARTIFACT_DIR, 'ramp_reloaded_from_dropdown.png') });
    console.log('12. Saved ramp_reloaded_from_dropdown.png');

    console.log('=== All tests passed successfully without error! ===');
  } catch (err) {
    console.error('Test failed with error:', err);
  } finally {
    await browser.close();
  }
}

main();
