/** main.js - Application entrypoint with domain switcher and diagram upload studio. */
import './style.css';
import { loadScene }        from './core/sceneLoader.js';
import { createSimulation } from './core/sceneRouter.js';
import { OverlayStage }     from './core/overlayStage.js';
import { uploadDiagramFile, analyzeDiagram } from './core/diagramAnalyzer.js';

const SCENES = {
  mechanics: '/scenes/kinematics/physics_scene.json',
  optics:    '/scenes/optics/thin_lens_scene.json',
};

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
    const isOptics = scene?.simulation?.domain === 'optics' || scene?.simulation_type === 'optics';
    const isMechanics = scene?.simulation?.domain === 'mechanics' || scene?.simulation_type === 'kinematics';
    const resolvedDomain = isOptics ? 'optics' : (isMechanics ? 'mechanics' : domain);

    setActive(resolvedDomain === 'optics' ? 'switch-optics' : 'switch-mechanics');
    currentController = createSimulation(scene, currentStage);
    console.log('[Main] Loaded simulation domain:', resolvedDomain, scene);
  } catch (err) {
    console.error('[Main] Failed to load domain:', domain, err);
  }
}

function setActive(id) {
  ['switch-mechanics', 'switch-optics'].forEach(btnId => {
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
  if (e.target === btnChangeImage) {
    fileInput.click();
    return;
  }
  if (!uploadedImageUrl) {
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
  uploadedFile = file;
  const localUrl = URL.createObjectURL(file);
  const img = new Image();
  img.onload = () => {
    setPreview(file.name, localUrl, img.naturalWidth, img.naturalHeight);
  };
  img.src = localUrl;
}

// Preset Pills Handler
const scenarioSelect = document.getElementById('upload-scenario-select');

document.querySelectorAll('.preset-pill').forEach(pill => {
  pill.addEventListener('click', () => {
    const preset = pill.dataset.preset;
    if (preset === 'snell') {
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
    } else if (preset === 'pendulum_test1') {
      setPreview('test1.jpg', '/uploads/test1.jpg', 797, 652);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'pendulum';
    } else if (preset === 'projectile_test') {
      setPreview('test.jpg', '/uploads/test.jpg', 700, 467);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'projectile';
    } else if (preset === 'prism') {
      setPreview('prism_diagram.png', '/scenes/optics/prism_scene.json', 800, 600);
      domainSelect.value = 'optics';
      if (scenarioSelect) scenarioSelect.value = 'prism';
    } else if (preset === 'spring') {
      setPreview('with_spring.png', '/scenes/kinematics/with_spring.png', 800, 600);
      domainSelect.value = 'mechanics';
      if (scenarioSelect) scenarioSelect.value = 'spring_mass';
    }
  });
});

domainSelect?.addEventListener('change', () => {
  opticsOpts.style.display = domainSelect.value === 'mechanics' ? 'none' : 'flex';
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
    let finalImageUrl = uploadedImageUrl;

    // If actual file was uploaded, upload it to the backend
    if (uploadedFile) {
      updateProgress('Uploading diagram to backend...', 20);
      const upRes = await uploadDiagramFile(uploadedFile);
      if (upRes.success && upRes.image_url) {
        finalImageUrl = upRes.image_url;
      }
    }

    // Run AI / CV analysis
    const domainChoice = domainSelect.value;
    const scenarioChoice = scenarioSelect?.value || 'auto';
    const focalCm = parseFloat(focalInput.value) || 20.0;
    const result = await analyzeDiagram(
      finalImageUrl,
      domainChoice,
      {
        scenario: scenarioChoice,
        focalLengthCm: focalCm,
      },
      updateProgress
    );

    setTimeout(() => {
      closeModal();
      bootstrap(result.domain, result.scene);
    }, 400);
  } catch (err) {
    console.error('[Upload] Analysis error:', err);
    progressStatus.textContent = 'Analysis error. Falling back to default scene...';
    setTimeout(closeModal, 1500);
  }
});

// Boot with kinematics by default
setActive('switch-mechanics');
bootstrap('mechanics');
