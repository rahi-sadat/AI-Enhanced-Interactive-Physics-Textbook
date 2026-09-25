/**
 * UploadService.js — PR-04 Real Image Ingestion Client
 *
 * Sends actual File bytes to /api/ingest (multipart/form-data).
 * The server creates SourceAsset → PageIR → BookIR → PhysicsCompiler.
 *
 * Rules:
 *   - Always sends actual bytes (never just a URL string).
 *   - Filename is metadata only on both sides.
 *   - Unknown images always return UNRESOLVED — never a fallback simulation.
 *   - Keeps track of the ingestion result so the frontend can display
 *     PageIR and BookIR for inspection.
 */

export class UploadService {
  /**
   * Ingests a File through the PR-04 /api/ingest endpoint.
   *
   * @param {File} file - The actual File object from the file input.
   * @param {function(string, number): void} onProgress - Progress callback (text, percent).
   * @returns {Promise<IngestResult>}
   */
  static async ingest(file, onProgress = () => {}) {
    onProgress('Preparing upload...', 5);

    if (!file || (!(file instanceof File) && !(file instanceof Blob))) {
      throw new TypeError('ingest() requires a File or Blob object');
    }

    const formData = new FormData();
    formData.append('file', file);

    onProgress('Uploading image bytes to server...', 20);

    let res;
    try {
      res = await fetch('/api/ingest', {
        method: 'POST',
        body: formData,
        // Do NOT set Content-Type header — browser sets it with boundary automatically
      });
    } catch (networkErr) {
      if (networkErr.message === 'Failed to fetch' || networkErr.name === 'TypeError') {
        throw new Error('Backend server is offline (port 8000). Please ensure the FastAPI backend is running via "python apps/api/main.py".');
      }
      throw new Error(`Network error during upload: ${networkErr.message}`);
    }

    if (!res.ok) {
      let detail = `Server returned HTTP ${res.status}`;
      try {
        const errBody = await res.json();
        detail = errBody.detail || detail;
      } catch (_) {}
      throw new Error(detail);
    }

    onProgress('Processing ingestion pipeline...', 60);

    const data = await res.json();

    onProgress('Ingestion complete', 100);

    return new IngestResult(data);
  }
}

/**
 * IngestResult — wraps the /api/ingest response envelope.
 *
 * Provides typed accessors for SourceAsset, PageIR, BookIR, and compiler result.
 */
export class IngestResult {
  /** @param {object} envelope - Raw JSON response from /api/ingest */
  constructor(envelope) {
    this._env = envelope;
  }

  /** @returns {boolean} */
  get success() { return Boolean(this._env.success); }

  /** Frontend-accessible URL for the uploaded image (served by backend). */
  get imageUrl() { return this._env.image_url || ''; }

  /** @returns {'unresolved'|'needs-review'|'unsupported'|'ready'} */
  get status() {
    return (this._env.status || this._env.compiler?.status || 'unresolved').toLowerCase().replace('_', '-');
  }

  /** @returns {string|null} */
  get domain() {
    return this._env.domain || this._env.book_ir?.domain || null;
  }

  /** @returns {string|null} */
  get scenario() {
    return this._env.scenario || this._env.book_ir?.subtype || null;
  }

  /** @returns {object|null} PhysicsScene if status === 'ready', otherwise null. */
  get scene() {
    return this._env.scene || this._env.compiler?.scene || null;
  }

  /** @returns {number} Native image width in source pixels. */
  get widthPx() { return this._env.width || 0; }

  /** @returns {number} Native image height in source pixels. */
  get heightPx() { return this._env.height || 0; }

  /** @returns {object} SourceAsset identity. */
  get sourceAsset() { return this._env.source_asset || {}; }

  /** @returns {object} PageIR in source_px. */
  get pageIR() { return this._env.page_ir || {}; }

  /** @returns {object} BookIR — semantic understanding. */
  get bookIR() { return this._env.book_ir || {}; }

  /** @returns {object} PhysicsCompilerResult. */
  get compiler() { return this._env.compiler || {}; }

  /** @returns {Array} Issues from the pipeline. */
  get issues() { return this._env.issues || []; }

  /** @returns {boolean} True only when a runnable scene is available. */
  get isReady() { return this.status === 'ready' && this.scene !== null; }

  /** @returns {boolean} True when physics was not understood or unresolved. */
  get isUnresolved() { return this.status === 'unresolved'; }

  /** @returns {string} Semantic classification status. */
  get classification() {
    return this.bookIR?.provenance?.classification || (this.isReady ? 'supported' : 'unknown');
  }

  /** @returns {Array} Semantic entities identified by VLM. */
  get entities() { return this.bookIR?.entities || []; }

  /** @returns {Array} Semantic relationships identified by VLM. */
  get relationships() { return this.bookIR?.relationships || []; }

  /** @returns {Array} Visible text labels (unverified candidate evidence). */
  get visibleLabels() { return this.bookIR?.provenance?.visible_labels || []; }

  /** @returns {Array} Alternative candidate interpretations. */
  get candidates() { return this.bookIR?.provenance?.candidates || []; }

  /** @returns {object} Confidence breakdown. */
  get confidence() { return this.bookIR?.confidence || {}; }

  /** @returns {string} Human-readable status message. */
  get statusMessage() {
    switch (this.status) {
      case 'ready':
        return 'Physics understood — interactive simulation ready.';
      case 'needs-review':
        if (this.domain && this.scenario) {
          return `Recognized ${this.domain} / ${this.scenario} — precise extraction needed before simulation.`;
        }
        return 'Physics partially understood — manual review required.';
      case 'unsupported':
        return 'Physics concept identified but no simulation solver is currently available for this topic.';
      case 'unresolved':
      default:
        return this.bookIR?.statusNotes || 'Image could not be identified as a supported physics concept.';
    }
  }
}

