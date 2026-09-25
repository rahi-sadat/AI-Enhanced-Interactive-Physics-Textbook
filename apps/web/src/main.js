/** main.js - Application entrypoint with domain switcher and diagram upload studio. */
import './style.css';
import { loadScene }        from '@engine/core/sceneLoader.js';
import { createLegacySimulation } from './features/simulations/legacy/legacySceneRouter.js';
import { OverlayStage }     from './features/simulations/core/overlayStage.js';
import { uploadDiagramFile, analyzeDiagram } from './features/simulations/core/diagramAnalyzer.js';
import { InteractiveFigure } from './components/InteractiveFigure.js';
// PR-04: Real image ingestion pipeline
import { UploadService }    from './features/simulations/core/UploadService.js';
import { IRDebugPanel }     from './features/simulations/core/IRDebugPanel.js';

const SCENES = {
  mechanics: '/scenes/kinematics/physics_scene.json',
  optics:    '/scenes/optics/thin_lens_scene.json',
  circuits:  '/scenes/circuits/circuit1_scene.json',
};

export function showDomainControls(domain) {
  const mc = document.getElementById('mechanics-controls');
  const oc = document.getElementById('optics-controls');
  const cc = document.getElementById('circuit-controls');
  if (mc) mc.style.display = (domain === 'mechanics') ? 'flex' : 'none';
  if (oc) oc.style.display = (domain === 'optics') ? 'flex' : 'none';
  if (cc) cc.style.display = (domain === 'circuits') ? 'block' : 'none';
}

let currentController = null;
let currentStage = null;
let uploadedFile = null;
let uploadedImageUrl = null;

export async function bootstrap(domain, sceneDataOrUrl = null) {
  try {
    currentController?.destroy?.();
    currentController = null;

    currentStage = new OverlayStage();
    currentStage.clearOverlay();

    let scene;
    if (sceneDataOrUrl && typeof sceneDataOrUrl === 'object') {
      scene = sceneDataOrUrl;
    } else {
      const url = typeof sceneDataOrUrl === 'string'
        ? sceneDataOrUrl
        : (SCENES[domain] || SCENES.mechanics);
      scene = await loadScene(url);
    }

    // Auto-detect domain from scene if not explicitly forced
    const isCircuits = scene?.simulation?.domain === 'circuits' || scene?.simulation_type === 'circuits';
    const isOptics = scene?.simulation?.domain === 'optics' || scene?.simulation_type === 'optics';
    const isMechanics = scene?.simulation?.domain === 'mechanics' || scene?.simulation_type === 'kinematics';
    const resolvedDomain = isCircuits ? 'circuits' : (isOptics ? 'optics' : (isMechanics ? 'mechanics' : domain));

    let activeBtnId = 'switch-mechanics';
    if (resolvedDomain === 'circuits') activeBtnId = 'switch-circuits';
    else if (resolvedDomain === 'optics') activeBtnId = 'switch-optics';

    setActive(activeBtnId);
    showDomainControls(resolvedDomain);
    currentController = createLegacySimulation(scene, currentStage);
    console.log('[Main] Loaded simulation domain:', resolvedDomain, scene);
  } catch (err) {
    console.error('[Main] Failed to load domain:', domain, err);
  }
}

function setActive(id) {
  ['switch-mechanics', 'switch-optics', 'switch-circuits'].forEach(btnId => {
    const btn = document.getElementById(btnId);
    if (btn) {
      btn.classList.toggle('active', btnId === id);
      btn.setAttribute('aria-selected', String(btnId === id));
    }
  });
}

document.getElementById('switch-mechanics')?.addEventListener('click', () => {
  setActive('switch-mechanics');
  bootstrap('mechanics');
});

document.getElementById('switch-optics')?.addEventListener('click', () => {
  setActive('switch-optics');
  bootstrap('optics');
});

document.getElementById('switch-circuits')?.addEventListener('click', () => {
  setActive('switch-circuits');
  bootstrap('circuits');
});

// ===================================================================
// DIAGRAM UPLOAD STUDIO & SIMULATION GENERATOR CONTROLLER
// ===================================================================

const modal = document.getElementById('upload-modal');
const btnOpenUpload = document.getElementById('btn-open-upload');
const btnCloseModal = document.getElementById('btn-close-modal');
const btnCancelModal = document.getElementById('btn-cancel-modal');
const btnGenerateSim = document.getElementById('btn-generate-sim');

const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const dropzonePrompt = document.getElementById('dropzone-prompt');
const dropzonePreview = document.getElementById('dropzone-preview');
const previewImage = document.getElementById('preview-image');
const previewFilename = document.getElementById('preview-filename');
const previewDims = document.getElementById('preview-dims');
const btnChangeImage = document.getElementById('btn-change-image');

const domainSelect = document.getElementById('upload-domain-select');
const opticsOpts = document.getElementById('upload-optics-opts');
const focalInput = document.getElementById('upload-focal-cm');

const progressArea = document.getElementById('upload-progress-area');
const progressFill = document.getElementById('upload-progress-fill');
const progressStatus = document.getElementById('upload-progress-status');

function openModal() {
  modal.style.display = 'flex';
  resetUploadState();
}

function closeModal() {
  modal.style.display = 'none';
  resetUploadState();
}

function resetUploadState() {
  uploadedFile = null;
  uploadedImageUrl = null;
  if (fileInput) fileInput.value = '';
  dropzonePrompt.style.display = 'block';
  dropzonePreview.style.display = 'none';
  btnGenerateSim.disabled = true;
  progressArea.style.display = 'none';
  progressFill.style.width = '0%';
}

function setPreview(name, url, w, h) {
  previewFilename.textContent = name;
  previewDims.textContent = `${w} × ${h} px`;
  previewImage.src = url;
  dropzonePrompt.style.display = 'none';
  dropzonePreview.style.display = 'flex';
  btnGenerateSim.disabled = false;
  uploadedImageUrl = url;
}

btnOpenUpload?.addEventListener('click', openModal);
btnCloseModal?.addEventListener('click', closeModal);
btnCancelModal?.addEventListener('click', closeModal);

modal?.addEventListener('click', (e) => {
  if (e.target === modal) closeModal();
});

// Dropzone click & drag
dropzone?.addEventListener('click', (e) => {
  if (e.target === btnChangeImage || btnChangeImage?.contains(e.target)) {
    if (fileInput) fileInput.value = '';
    fileInput.click();
    return;
  }
  if (!uploadedImageUrl) {
    if (fileInput) fileInput.value = '';
    fileInput.click();
  }
});

dropzone?.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone?.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone?.addEventListener('drop', (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  if (e.dataTransfer.files?.length > 0) {
    handleFile(e.dataTransfer.files[0]);
  }
});

fileInput?.addEventListener('change', () => {
  if (fileInput.files?.length > 0) {
    handleFile(fileInput.files[0]);
  }
});

async function handleFile(file) {
  if (!file) return;
  uploadedFile = file;
  const localUrl = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    setPreview(file.name, localUrl, img.naturalWidth, img.naturalHeight);
  };
  img.onerror = () => {
    console.error('Failed to decode image preview for file:', file.name);
    previewFilename.textContent = file.name;
    previewDims.textContent = 'Invalid / unreadable image';
    previewImage.src = '';
    dropzonePrompt.style.display = 'none';
    dropzonePreview.style.display = 'flex';
    btnGenerateSim.disabled = true;
  };
  img.src = localUrl;
}

// Preset Pills Handler
const scenarioSelect = document.getElementById('upload-scenario-select');

document.querySelectorAll('.preset-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    uploadedFile = null; // Clear real uploaded file so presets use legacy path
    if (fileInput) fileInput.value = '';
    const preset = pill.dataset.preset;
    if (preset === 'circuit1') {
      setPreview('circuit1.png', '/uploads/circuit1.png', 484, 399);
      domainSelect.value = 'circuits';
      if (scenarioSelect) scenarioSelect.value = 'circuit1';
    } else if (preset === 'circuit2') {
      setPreview('circuit2.png', '/uploads/circuit2.png', 878, 593);
      domainSelect.value = 'circuits';
      if (scenarioSelect) scenarioSelect.value = 'circuit2';
    } else if (preset === 'circuit3') {
      setPreview('circuit3.png', '/uploads/circuit3.png', 529, 273);
      domainSelect.value = 'circuits';
      if (scenarioSelect) scenarioSelect.value = 'circuit3';
    } else if (preset === 'circuit4') {
      setPreview('circuit4.png', '/uploads/circuit4.png', 1272, 581);
      domainSelect.value = 'circuits';
      if (scenarioSelect) scenarioSelect.value = 'circuit4';
    } else if (preset === 'snell_water') {
      setPreview('diagram_0ae6ee8e.png', '/uploads/diagram_0ae6ee8e.png', 1536, 1024);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'interface_refraction';
    } else if (preset === 'snell') {
      setPreview('diagram_7dcbe9c0.png', '/uploads/diagram_7dcbe9c0.png', 393, 328);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'interface_refraction';
    } else if (preset === 'mirror_cff') {
      setPreview('diagram_cff33623.png', '/uploads/diagram_cff33623.png', 553, 469);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'mirror';
    } else if (preset === 'lens_cece') {
      setPreview('diagram_ceceeb1a.jpg', '/uploads/diagram_ceceeb1a.jpg', 1024, 768);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'thin_lens';
    } else if (preset === 'newtons_cradle') {
      setPreview('pendulum.png', '/uploads/pendulum.png', 387, 367);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'newtons_cradle';
    } else if (preset === 'projectile_test') {
      setPreview('test.jpg', '/uploads/test.jpg', 700, 467);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'projectile';
    } else if (preset === 'prism') {
      setPreview('prism_diagram.png', '/scenes/optics/prism_scene.json', 800, 600);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'prism';
    } else if (preset === 'spring') {
      setPreview('with_spring.png', '/scenes/kinematics/with_spring.png', 855, 686);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'incline';
    }
  });
});

domainSelect?.addEventListener('change', () => {
  opticsOpts.style.display = domainSelect.value === 'optics' ? 'flex' : 'none';
});

// GENERATE SIMULATION BUTTON
btnGenerateSim?.addEventListener('click', async () => {
  if (!uploadedImageUrl) return;

  btnGenerateSim.disabled = true;
  progressArea.style.display = 'flex';

  const updateProgress = (text, percent) => {
    progressStatus.textContent = text;
    progressFill.style.width = `${percent}%`;
  };

  try {
    // ---------------------------------------------------------------
    // PR-04 PATH: actual uploaded File → /api/ingest (real bytes sent)
    // ---------------------------------------------------------------
    if (uploadedFile) {
      updateProgress('Sending image to ingestion pipeline...', 15);
      let ingestResult;
      try {
        ingestResult = await UploadService.ingest(uploadedFile, updateProgress);
      } catch (ingestErr) {
        // FATAL FOR USER UPLOAD: NEVER fall through to legacy analysis!
        console.error('[PR-04] Ingestion failed:', ingestErr);
        btnGenerateSim.disabled = false;
        progressStatus.textContent = `Upload / analysis failed: ${ingestErr.message || ingestErr}`;
        return; // STOP! No legacy rescue for uploaded files.
      }

      // Update debug panel
      if (irDebugPanel) irDebugPanel.update(ingestResult);

      updateProgress(ingestResult.statusMessage, 100);

      if (ingestResult.isReady && ingestResult.scene) {
        // Backend understood the physics — launch simulation
        const scene = ingestResult.scene;
        if (!scene.visual) scene.visual = {};
        if (!scene.visual.background_url) {
          scene.visual.background_url = ingestResult.imageUrl;
        }
        setTimeout(() => {
          closeModal();
          if (activeFigure && (ingestResult.domain === 'optics' || ingestResult.domain === 'circuits')) {
            setPlatformMode('runtime');
            activeFigure.load(scene);
          } else {
            bootstrap(ingestResult.domain, scene);
          }
        }, 400);
      } else {
        // Honest non-ready response — show informative message without fabricating
        btnGenerateSim.disabled = false;
        const issueTexts = ingestResult.issues.map(i => i.message || i.code).join('; ');
        progressStatus.textContent =
          ingestResult.statusMessage +
          (issueTexts ? ` (${issueTexts})` : '');
      }
      return; // STOP! Complete path for user-uploaded file.
    }

    // ---------------------------------------------------------------
    // LEGACY PATH: pre-compiled preset scenes (no uploaded file)
    // ---------------------------------------------------------------
    let finalImageUrl = uploadedImageUrl;

    // If actual file was uploaded, upload it to the backend
    if (uploadedFile) {
      updateProgress('Uploading diagram to backend...', 20);
      const upRes = await uploadDiagramFile(uploadedFile);
      if (upRes.success && upRes.image_url) {
        finalImageUrl = upRes.image_url;
      }
    }

    // Check if selecting a pre-compiled textbook scene without custom file upload
    const PRESET_SCENES = {
      circuit1: { domain: 'circuits', url: '/scenes/circuits/circuit1_scene.json' },
      circuit2: { domain: 'circuits', url: '/scenes/circuits/circuit2_scene.json' },
      circuit3: { domain: 'circuits', url: '/scenes/circuits/circuit3_scene.json' },
      circuit4: { domain: 'circuits', url: '/scenes/circuits/circuit4_scene.json' },
      bridge: { domain: 'circuits', url: '/scenes/circuits/bridge_scene.json' },
      series_parallel: { domain: 'circuits', url: '/scenes/circuits/series_parallel_scene.json' },
      newtons_cradle: { domain: 'mechanics', url: '/scenes/kinematics/newtons_cradle_scene.json' },
      incline: { domain: 'mechanics', url: '/scenes/kinematics/physics_scene.json' },
    };

    const scenarioChoice = scenarioSelect?.value || 'auto';

    if (!uploadedFile && PRESET_SCENES[scenarioChoice]) {
      updateProgress('Loading pre-compiled textbook scenario...', 80);
      const presetInfo = PRESET_SCENES[scenarioChoice];
      const pRes = await fetch(presetInfo.url + '?t=' + Date.now());
      const pScene = await pRes.json();
      setTimeout(() => {
        closeModal();
        if (activeFigure && (presetInfo.domain === 'optics' || presetInfo.domain === 'circuits')) {
          setPlatformMode('runtime');
          activeFigure.load(pScene);
        } else {
          bootstrap(presetInfo.domain, pScene);
        }
      }, 300);
      return;
    }

    // Helper to display analysis issues in the review modal without closing it
    const renderAnalysisIssues = (res) => {
      btnGenerateSim.disabled = false;
      if (!res) {
        progressStatus.textContent = 'Analysis returned no response.';
        return;
      }
      const issues = res.issues || [];
      if (issues.length > 0) {
        const msgs = issues.map((i) => i.message || i.code).join(' | ');
        progressStatus.textContent = `Review required (${res.status}): ${msgs}`;
      } else if (res.status === 'unsupported') {
        progressStatus.textContent = `Unsupported scenario '${res.scenario || 'unknown'}'. Scene generation withheld.`;
      } else if (res.status === 'needs_review') {
        progressStatus.textContent = 'Analysis requires review. No simulation could be verified from evidence.';
      } else {
        progressStatus.textContent = `Status: ${res.status}. Scene generation withheld.`;
      }
    };

    // Run AI / CV analysis
    const domainChoice = domainSelect.value;
    const scenarioChoiceVal = scenarioChoice;
    const parsedFocal = Number.parseFloat(focalInput?.value);
    const focalCm = Number.isFinite(parsedFocal) ? parsedFocal : null;
    const result = await analyzeDiagram(
      finalImageUrl,
      domainChoice,
      {
        scenario: scenarioChoiceVal,
        focalLengthCm: focalCm,
      },
      updateProgress
    );

    // Strict gate: only ready responses with verified scenes proceed to bootstrap
    if (!result || result.status !== 'ready' || !result.scene) {
      renderAnalysisIssues(result);
      return;
    }

    setTimeout(() => {
      closeModal();
      if (uploadedImageUrl && result?.scene) {
        if (!result.scene.visual) result.scene.visual = {};
        if (!result.scene.visual.background_url) {
          result.scene.visual.background_url = uploadedImageUrl;
        }
      }
      if (activeFigure && (result.domain === 'optics' || result.domain === 'circuits')) {
        setPlatformMode('runtime');
        activeFigure.load(result.scene);
      } else {
        bootstrap(result.domain, result.scene);
      }
    }, 400);
  } catch (err) {
    console.error('[Upload] Analysis error:', err);
    progressStatus.textContent = `Analysis error: ${err.message || 'Failed to process diagram.'}`;
    btnGenerateSim.disabled = false;
  }
});

// Boot with kinematics by default
setActive('switch-mechanics');
bootstrap('mechanics');

// ===================================================================
// PLATFORM SPINE DEMO: INTERACTIVE FIGURE RUNTIME
// ===================================================================
const figureHost = document.getElementById('interactive-figure-container');
let activeFigure = null;

if (figureHost) {
  activeFigure = new InteractiveFigure(figureHost);
  activeFigure.load('/scenes/canonical/pendulum_figure.json');
}

// PR-04: IR Debug Panel (development/debug-only — guarded from students)
function isDevOrDebugMode() {
  if (typeof window === 'undefined') return false;
  if (window.__AUGMENTED_PHYSICS_DEBUG__ === true) return true;
  if (new URLSearchParams(window.location.search).get('debug') === 'true') return true;
  if (localStorage.getItem('augmented_physics_debug') === 'true') return true;
  if (import.meta.env && import.meta.env.DEV) return true;
  return false;
}

const irDebugHost = document.getElementById('ir-debug-panel');
const irDebugSection = document.getElementById('ir-debug-section');
let irDebugPanel = null;
if (irDebugHost) {
  irDebugPanel = new IRDebugPanel(irDebugHost);
  const _origUpdate = irDebugPanel.update.bind(irDebugPanel);
  irDebugPanel.update = (result) => {
    _origUpdate(result);
    // Explicit safeguard: only reveal debug section in dev or debug mode
    if (irDebugSection && isDevOrDebugMode()) {
      irDebugSection.style.display = 'block';
    }
  };
}


const btnModeRuntime = document.getElementById('view-mode-runtime');
const btnModeStudio = document.getElementById('view-mode-studio');
const runtimeFigSelector = document.getElementById('runtime-figure-selector');
const studioLayout = document.getElementById('legacy-studio-layout');

function setPlatformMode(mode) {
  const isRuntime = mode === 'runtime';
  if (btnModeRuntime) {
    btnModeRuntime.classList.toggle('active', isRuntime);
    btnModeRuntime.style.background = isRuntime ? 'rgba(56, 189, 248, 0.18)' : 'transparent';
    btnModeRuntime.style.borderColor = isRuntime ? 'rgba(56, 189, 248, 0.5)' : 'rgba(148, 163, 184, 0.2)';
    btnModeRuntime.style.color = isRuntime ? '#38bdf8' : '#94a3b8';
  }
  if (btnModeStudio) {
    btnModeStudio.classList.toggle('active', !isRuntime);
    btnModeStudio.style.background = !isRuntime ? 'rgba(56, 189, 248, 0.18)' : 'transparent';
    btnModeStudio.style.borderColor = !isRuntime ? 'rgba(56, 189, 248, 0.5)' : 'rgba(148, 163, 184, 0.2)';
    btnModeStudio.style.color = !isRuntime ? '#38bdf8' : '#94a3b8';
  }
  if (figureHost) figureHost.style.display = isRuntime ? 'block' : 'none';
  if (runtimeFigSelector) runtimeFigSelector.style.display = isRuntime ? 'flex' : 'none';
  if (studioLayout) studioLayout.style.display = !isRuntime ? 'flex' : 'none';
}

btnModeRuntime?.addEventListener('click', () => setPlatformMode('runtime'));
btnModeStudio?.addEventListener('click', () => setPlatformMode('studio'));

// Canonical Verification Figure Switcher
const figPills = [
  { id: 'fig-btn-pendulum',   url: '/scenes/canonical/pendulum_figure.json' },
  { id: 'fig-btn-lens',       url: '/scenes/canonical/lens_figure.json' },
  { id: 'fig-btn-circuit',    url: '/scenes/canonical/circuit_figure.json' },
  { id: 'fig-btn-projectile', url: '/scenes/canonical/projectile_figure.json' }
];

figPills.forEach(({ id, url }) => {
  const btn = document.getElementById(id);
  btn?.addEventListener('click', () => {
    figPills.forEach(p => {
      const b = document.getElementById(p.id);
      if (b) {
        b.style.background = (p.id === id) ? '#0284c7' : 'rgba(30, 41, 59, 0.8)';
        b.style.borderColor = (p.id === id) ? '#38bdf8' : 'rgba(148, 163, 184, 0.3)';
        b.style.color = (p.id === id) ? '#ffffff' : '#e2e8f0';
      }
    });
    activeFigure?.load(url);
  });
});

