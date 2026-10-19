import fs from 'fs';
import path from 'path';
import assert from 'node:assert/strict';

async function run() {
  const webPort = process.env.PHASE4_WEB_PORT || '5173';
  console.log('===========================================================');
  console.log('  LIVE MANUAL BROWSER VERIFICATION OF PR-08 (CHROME CDP)  ');
  console.log('===========================================================');

  // 1. Connect to Chrome CDP
  const targetsRes = await fetch('http://localhost:9222/json');
  const targets = await targetsRes.json();
  const pageTarget = targets.find(t => t.type === 'page' && t.url.includes(`:${webPort}`));

  if (!pageTarget) {
    throw new Error(`Could not find AugmentedPhysics tab in Chrome (port ${webPort})`);
  }

  console.log('[CDP] Connected to tab:', pageTarget.title);
  const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);

  let id = 1;
  const pending = new Map();

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.id && pending.has(data.id)) {
      const { resolve, reject } = pending.get(data.id);
      pending.delete(data.id);
      if (data.error) reject(data.error);
      else resolve(data.result);
    }
  };

  await new Promise(resolve => ws.onopen = resolve);
  console.log('[CDP] WebSocket connection to browser debugger established.');

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  await send('Page.enable');
  await send('Runtime.enable');
  await send('DOM.enable');

  async function evalInPage(expression) {
    const res = await send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true
    });
    if (res.exceptionDetails) {
      throw new Error(`Eval exception: ${JSON.stringify(res.exceptionDetails)}`);
    }
    return res.result?.value;
  }

  async function sleep(ms) {
    return new Promise(r => setTimeout(r, ms));
  }

  async function captureScreenshot(filename) {
    try {
      const res = await Promise.race([
        send('Page.captureScreenshot', { format: 'png' }),
        new Promise((_, rej) => setTimeout(() => rej(new Error('Screenshot timeout')), 5000))
      ]);
      const buffer = Buffer.from(res.data, 'base64');
      const outPath = path.resolve('storage', 'generated', 'phase4-browser', filename);
      fs.mkdirSync(path.dirname(outPath), { recursive: true });
      fs.writeFileSync(outPath, buffer);
      console.log(`[Screenshot saved]: ${outPath} (${buffer.length} bytes)`);
    } catch (e) {
      console.warn(`[Screenshot warning]: ${e.message}`);
    }
  }

  // -------------------------------------------------------------
  // STEP 1: Verify Initial Browser State
  // -------------------------------------------------------------
  console.log('\n[Step 1] Verifying initial browser environment...');
  const title = await evalInPage('document.title');
  const hasOrch = await evalInPage('typeof window.__orchestrator !== "undefined"');
  const hasModal = await evalInPage('typeof window.__reviewModal !== "undefined"');
  assert.ok(hasOrch && hasModal, 'Web app did not initialize');
  console.log('✓ Document Title:', title);
  console.log('✓ SimulationOrchestrator exposed on window:', hasOrch);
  console.log('✓ PhysicsReviewModal exposed on window:', hasModal);

  // -------------------------------------------------------------
  // STEP 2: Ingest Diagram Image via PR-08 Orchestrator
  // -------------------------------------------------------------
  console.log('\n[Step 2] Ingesting real textbook diagram (pendulum_sketch_raw.png)...');
  const imageBytes = fs.readFileSync('tests/fixtures/unseen/mechanics/pendulum_sketch_raw.png');
  const base64Data = imageBytes.toString('base64');

  await evalInPage(`
    (async () => {
      const base64 = "${base64Data}";
      const byteChars = atob(base64);
      const byteNums = new Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) byteNums[i] = byteChars.charCodeAt(i);
      const byteArray = new Uint8Array(byteNums);
      const blob = new Blob([byteArray], { type: "image/png" });
      const file = new File([blob], "pendulum_sketch_raw.png", { type: "image/png" });

      window.__testFile = file;
      window.__orchestrator.startWithFile(file).catch(e => console.error("Orchestrator startWithFile error:", e));
    })()
  `);

  console.log('Waiting for backend perception pipeline (OpenCV, SAM 2, RapidOCR)...');
  let reachedNeedsReview = false;
  for (let i = 0; i < 120; i++) {
    await sleep(1000);
    const orchState = await evalInPage('window.__orchestrator.state');
    console.log(`  [T+${i}s] Orchestrator state: "${orchState}"`);
    if (orchState === 'NEEDS_REVIEW') {
      reachedNeedsReview = true;
      break;
    }
  }

  if (!reachedNeedsReview) {
    const lastErr = await evalInPage('window.__orchestrator.currentError');
    throw new Error(`Orchestrator failed to reach NEEDS_REVIEW: ${lastErr}`);
  }
  console.log('✓ Orchestrator successfully reached NEEDS_REVIEW!');

  // -------------------------------------------------------------
  // STEP 3: Review Modal Opens & Displays Review Issues
  // -------------------------------------------------------------
  console.log('\n[Step 3] Opening PhysicsReviewModal...');
  await evalInPage('window.__reviewModal.open()');
  await sleep(600);

  const isModalVisible = await evalInPage('document.querySelector(".prm-backdrop")?.classList.contains("open")');
  assert.equal(isModalVisible, true, 'Evidence review did not open');
  console.log('✓ PhysicsReviewModal open:', isModalVisible);
  await captureScreenshot('manual_test_step3_review_modal.png');

  // Inspect issues in modal
  const issueCards = await evalInPage(`
    Array.from(document.querySelectorAll(".prm-issue-card")).map(card => ({
      param: card.querySelector(".prm-param-name")?.textContent?.trim(),
      hasPolicyBtn: !!card.querySelector('[data-action="apply-policy"]'),
      policyTitle: card.querySelector(".prm-policy-title")?.textContent?.trim(),
      hasManualInput: !!card.querySelector(".prm-input"),
      hasCandidate: !!card.querySelector('[data-action="confirm"]')
    }))
  `);
  console.log(`✓ Detected ${issueCards.length} review issue cards:`);
  issueCards.forEach((iss, idx) => {
    console.log(`   [${idx + 1}] Parameter: ${iss.param} | Policy: ${iss.policyTitle || 'None'} | Manual: ${iss.hasManualInput} | Candidate: ${iss.hasCandidate}`);
  });

  // -------------------------------------------------------------
  // STEP 4: Interactively Resolve Requirements via Review Modal
  // -------------------------------------------------------------
  console.log('\n[Step 4] Interactively resolving review issues...');

  // A. Submit manual length: 0.8 m
  console.log('  -> Submitting manual length: 0.8 m...');
  await evalInPage('window.__orchestrator.submitManualValue("length", 0.8, "m")');
  await sleep(1500);
  console.log('  ✓ Saved manual length');

  // B. Apply Gravity Policy
  console.log('  -> Applying modeling assumption: Standard Earth Gravity (policy_earth_gravity)...');
  await evalInPage('window.__orchestrator.applyPolicy("policy_earth_gravity", "gravity")');
  await sleep(1500);
  console.log('  ✓ Applied Earth Gravity policy');

  // C. Apply Mass Policy
  console.log('  -> Applying modeling assumption: Standard Reference Mass (policy_standard_mass)...');
  await evalInPage('window.__orchestrator.applyPolicy("policy_standard_mass", "mass")');
  await sleep(1500);
  console.log('  ✓ Applied Mass policy');

  // D. Apply Damping Policy
  console.log('  -> Applying modeling assumption: Ideal Zero Damping (policy_zero_damping)...');
  await evalInPage('window.__orchestrator.applyPolicy("policy_zero_damping", "damping")');
  await sleep(1500);
  console.log('  ✓ Applied Damping policy');

  // -------------------------------------------------------------
  // STEP 5: Verify Compilation Readiness & Ready Banner
  // -------------------------------------------------------------
  console.log('\n[Step 5] Checking compilation readiness & hero banner...');
  const stateAfterResolutions = await evalInPage('window.__orchestrator.state');
  assert.equal(stateAfterResolutions, 'READY_TO_SIMULATE', 'Review did not compile a scene');
  console.log('✓ Orchestrator State:', stateAfterResolutions);

  const hasReadyBanner = await evalInPage('!!document.querySelector(".prm-ready-banner")');
  const readyBannerTitle = await evalInPage('document.querySelector(".prm-ready-title")?.textContent?.trim()');
  const footerStartSimVisible = await evalInPage('document.querySelector(\'[data-el="btnStartSim"]\')?.style.display !== "none"');
  assert.ok(hasReadyBanner && footerStartSimVisible, 'Start action is missing');

  console.log('✓ Ready Banner Present in Review Dialog:', hasReadyBanner);
  console.log('✓ Ready Banner Title:', readyBannerTitle);
  console.log('✓ Footer Start Sim Button Visible:', footerStartSimVisible);

  await captureScreenshot('manual_test_step5_ready_to_simulate.png');

  // -------------------------------------------------------------
  // STEP 6: Decoupled Simulation Start
  // -------------------------------------------------------------
  console.log('\n[Step 6] Clicking "▶ Start Simulation" button in Review Dialog...');
  await evalInPage(`
    (() => {
      const bannerBtn = document.querySelector('[data-action="start-sim-banner"]');
      const footerBtn = document.querySelector('[data-el="btnStartSim"]');
      if (bannerBtn) bannerBtn.click();
      else if (footerBtn) footerBtn.click();
    })()
  `);
  await sleep(1000);

  const finalState = await evalInPage('window.__orchestrator.state');
  assert.equal(finalState, 'SIMULATING', 'Explicit start did not transition');
  const modalOpenAfter = await evalInPage('document.querySelector(".prm-backdrop")?.classList.contains("open")');
  console.log('✓ Orchestrator State is now:', finalState);
  console.log('✓ ReviewModal closed automatically:', !modalOpenAfter);

  // -------------------------------------------------------------
  // STEP 7: Verify Live Simulation on Stage
  // -------------------------------------------------------------
  console.log('\n[Step 7] Verifying live simulation on stage...');
  const figureInfo = await evalInPage(`
    (() => {
      const fig = window.__activeFigure;
      return {
        hasFigure: !!fig,
        hasScene: !!fig?.scene,
        domain: fig?.scene?.domain,
        subtype: fig?.scene?.subtype,
        parameters: fig?.scene?.parameters,
        isRunning: fig?.runtime?.getState?.()?.running || false
      };
    })()
  `);
  assert.equal(figureInfo.domain, 'mechanics');
  assert.equal(figureInfo.subtype, 'pendulum');
  assert.equal(figureInfo.isRunning, true, 'Runtime did not play after Start Simulation');
  const alignment = await evalInPage(`(() => {
    const viewport = window.__activeFigure.viewport;
    const image = viewport._dom.image;
    const overlay = viewport._dom.overlay;
    const a = image.getBoundingClientRect();
    const b = overlay.getBoundingClientRect();
    return {
      loaded: image.complete && image.naturalWidth > 0,
      sourceWidth: viewport.sourceW,
      sourceHeight: viewport.sourceH,
      naturalWidth: image.naturalWidth,
      naturalHeight: image.naturalHeight,
      maxEdgeError: Math.max(...['left', 'top', 'right', 'bottom'].map(edge => Math.abs(a[edge] - b[edge])))
    };
  })()`);
  assert.equal(alignment.loaded, true, 'Source diagram image did not load');
  assert.equal(alignment.sourceWidth, alignment.naturalWidth, 'Source width differs from displayed image');
  assert.equal(alignment.sourceHeight, alignment.naturalHeight, 'Source height differs from displayed image');
  assert.ok(alignment.maxEdgeError <= 2, `Overlay edge mismatch: ${alignment.maxEdgeError}px`);
  console.log('✓ Source image and overlay edge error:', alignment.maxEdgeError, 'CSS px');
  console.log('✓ Active Figure Domain:', figureInfo.domain);
  console.log('✓ Active Figure Subtype:', figureInfo.subtype);
  console.log('✓ Simulation Running:', figureInfo.isRunning);
  console.log('✓ Length Parameter:', figureInfo.parameters?.length?.value, figureInfo.parameters?.length?.unit);
  console.log('✓ Gravity Parameter:', figureInfo.parameters?.gravity?.value, figureInfo.parameters?.gravity?.unit);

  await captureScreenshot('manual_test_step7_simulation_running.png');

  // -------------------------------------------------------------
  // STEP 8: Parameter Sliders & Reset to Textbook Values
  // -------------------------------------------------------------
  console.log('\n[Step 8] Testing parameter sliders and "Reset to textbook values"...');
  const resetBtnExists = await evalInPage('!!document.querySelector(".interactive-figure-root [data-el=btnReset]")');
  const reviewSetupBtnExists = await evalInPage('!!document.querySelector(".interactive-figure-root [data-el=btnReviewSetup]")');
  assert.ok(resetBtnExists && reviewSetupBtnExists, 'Figure controls are missing');
  console.log('✓ "Reset to textbook values" button exists:', resetBtnExists);
  console.log('✓ "✎ Review Setup" button exists:', reviewSetupBtnExists);

  // Update simulation length slider to 1.5 m
  console.log('  -> Simulating student slider experiment (Length 0.8 m -> 1.5 m)...');
  const beforeEvidence = await evalInPage('JSON.stringify(window.__orchestrator.bookIR)');
  await evalInPage(`(() => {
    const input = document.querySelector('.interactive-figure-root [data-param-key="length"] .if-val-input');
    if (!input) throw new Error('Length input is missing');
    input.value = '1.5';
    input.dispatchEvent(new Event('change', { bubbles: true }));
  })()`);
  const experimentalLength = await evalInPage('window.__activeFigure?.runtime?.scene?.parameters?.length?.value');
  assert.equal(experimentalLength, 1.5, 'Student parameter change did not reach runtime');
  const afterEvidence = await evalInPage('JSON.stringify(window.__orchestrator.bookIR)');
  assert.equal(afterEvidence, beforeEvidence, 'Exploration mutated BookIR evidence');
  console.log(`  ✓ Runtime slider length: ${experimentalLength} m`);
  console.log('  ✓ Grounded BookIR evidence remained unchanged');

  // Reset to textbook
  console.log('  -> Clicking "↺ Reset to textbook values"...');
  await evalInPage('document.querySelector(".interactive-figure-root [data-el=btnReset]").click()');
  await sleep(400);

  const restoredLength = await evalInPage('window.__activeFigure?.runtime?.scene?.parameters?.length?.value');
  assert.equal(restoredLength, 0.8, 'Reset did not restore the compiled value');
  console.log(`  ✓ Restored length back to textbook: ${restoredLength} m`);

  // -------------------------------------------------------------
  // STEP 9: Reopen Review Dialog from Active Simulation
  // -------------------------------------------------------------
  console.log('\n[Step 9] Clicking "✎ Review Setup" to verify reopening setup modal...');
  await evalInPage('document.querySelector(".interactive-figure-root [data-el=btnReviewSetup]").click()');
  await sleep(500);

  const modalReopened = await evalInPage('document.querySelector(".prm-backdrop")?.classList.contains("open")');
  assert.equal(modalReopened, true, 'Review Setup did not reopen');
  console.log('✓ ReviewModal reopened successfully:', modalReopened);

  const resolvedItemsCount = await evalInPage('document.querySelectorAll(".prm-resolved-item").length');
  console.log(`✓ Detected ${resolvedItemsCount} resolved parameters displayed with provenance badges`);

  await captureScreenshot('manual_test_step9_reopened_modal.png');

  // Close modal cleanly
  await evalInPage('document.querySelector(\'[data-el="btnClose"]\')?.click()');
  await sleep(400);

  console.log('\n===========================================================');
  console.log('  PENDULUM BROWSER ACCEPTANCE CHECK PASSED                  ');
  console.log('===========================================================');

  ws.close();
  process.exit(0);
}

run().catch(err => {
  console.error('\n*** MANUAL VERIFICATION ERROR ***', err);
  process.exit(1);
});
