/**
 * IRDebugPanel.js — Development-only PageIR / BookIR inspection panel.
 *
 * Renders an expandable panel showing:
 *   - SourceAsset (dimensions, sha256, MIME)
 *   - PageIR (coordinate space, regions, figures, text blocks)
 *   - BookIR (domain, subtype, entities, parameters, evidence, status)
 *   - Compiler result (status, issues)
 *
 * This is a DEVELOPMENT tool. It should not appear in the normal student UI.
 * It is only rendered when the host element with id="ir-debug-panel" exists.
 */

function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export class IRDebugPanel {
  /**
   * @param {HTMLElement} hostEl - Container element for the panel.
   */
  constructor(hostEl) {
    this._host = hostEl;
    this._render(null); // show empty state initially
  }

  /**
   * Update the panel with a new IngestResult.
   * @param {import('./UploadService.js').IngestResult} result
   */
  update(result) {
    this._render(result);
  }

  /** Clear the panel back to empty state. */
  clear() {
    this._render(null);
  }

  _render(result) {
    if (!this._host) return;

    if (!result) {
      this._host.innerHTML = `
        <div class="ir-debug-empty">
          <span style="color: #64748b; font-size: 0.85rem;">
            📋 IR Debug Panel — select and analyze an image to inspect PageIR / BookIR
          </span>
        </div>`;
      return;
    }

    const sa = result.sourceAsset || {};
    const pi = result.pageIR || {};
    const bi = result.bookIR || {};
    const cr = result.compiler || {};

    const statusColor = {
      'ready': '#22c55e',
      'needs-review': '#f59e0b',
      'unsupported': '#f97316',
      'unresolved': '#64748b',
    }[result.status] || '#64748b';

    const badge = (text, color) =>
      `<span style="display:inline-block;padding:2px 8px;border-radius:4px;background:${color}22;color:${color};font-size:0.78rem;font-weight:700;border:1px solid ${color}44;">${escapeHtml(text)}</span>`;

    const kv = (k, v, isRawHtml = false) =>
      `<div style="display:flex;gap:8px;margin:2px 0;">
         <span style="color:#64748b;min-width:140px;font-size:0.82rem;">${escapeHtml(k)}</span>
         <span style="color:#e2e8f0;font-size:0.82rem;word-break:break-all;">${v !== null && v !== undefined ? (isRawHtml ? v : escapeHtml(v)) : '<span style="color:#475569">null</span>'}</span>
       </div>`;

    const section = (title, content) =>
      `<details open style="margin:6px 0;border:1px solid rgba(148,163,184,0.15);border-radius:6px;overflow:hidden;">
         <summary style="padding:6px 10px;background:rgba(30,41,59,0.9);cursor:pointer;font-size:0.82rem;font-weight:600;color:#94a3b8;user-select:none;">${escapeHtml(title)}</summary>
         <div style="padding:8px 12px;background:rgba(15,23,42,0.7);">${content}</div>
       </details>`;

    const regions = (pi.regions || []).map(r =>
      kv(`${r.id} (${r.detectionMethod})`, `${r.label} @ (${r.x},${r.y}) ${r.width}×${r.height}px`)
    ).join('');

    const figures = (pi.figures || []).map(f =>
      kv(`${f.id} in ${f.regionId}`, `${f.width}×${f.height}px @ page(${f.pageX},${f.pageY}) — ${f.detectionMethod}`)
    ).join('');

    const entities = (bi.entities || []).map(e =>
      kv(`${e.id} (${e.type})`, e.label || '—')
    ).join('') || '<span style="color:#475569;font-size:0.82rem;">No entities identified</span>';

    const parameters = Object.entries(bi.parameters || {}).map(([k, v]) => {
      const val = typeof v === 'object' ? JSON.stringify(v) : String(v);
      return kv(k, val);
    }).join('') || '<span style="color:#475569;font-size:0.82rem;">No parameters extracted</span>';

    const issues = (cr.issues || []).map(i =>
      `<div style="color:#f87171;font-size:0.8rem;padding:2px 0;">⚠ [${escapeHtml(i.code)}] ${escapeHtml(i.message)}</div>`
    ).join('') || '<span style="color:#475569;font-size:0.82rem;">No issues</span>';

    this._host.innerHTML = `
      <div style="font-family:'Inter',sans-serif;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
          <span style="font-size:0.82rem;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:0.06em;">🔬 IR Debug Panel</span>
          ${badge(result.status ? result.status.toUpperCase() : 'UNKNOWN', statusColor)}
        </div>

        ${section('📦 SourceAsset', [
          kv('Asset ID', sa.id),
          kv('MIME Type', sa.mimeType),
          kv('Original Filename', `${escapeHtml(sa.originalFilename)} <span style="color:#475569;font-size:0.75rem;">(metadata only)</span>`, true),
          kv('Dimensions', `${sa.width_px} × ${sa.height_px} px (native source_px)`),
          kv('Byte Size', sa.byteSize ? `${(sa.byteSize / 1024).toFixed(1)} KB` : '—'),
          kv('SHA-256', `<span style="font-family:monospace;font-size:0.75rem;">${escapeHtml(sa.sha256?.slice(0, 16))}…</span> <span style="color:#475569;font-size:0.75rem;">(identity only, not routing)</span>`, true),
        ].join(''))}

        ${section('📄 PageIR', [
          kv('Version', pi.version),
          kv('Coordinate Space', pi.coordinateSpace?.type || '—'),
          kv('Source Dimensions', pi.source ? `${pi.source.width_px} × ${pi.source.height_px} px` : '—'),
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Regions:</div>',
          regions || '<span style="color:#475569;font-size:0.82rem;">None</span>',
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Figures:</div>',
          figures || '<span style="color:#475569;font-size:0.82rem;">None</span>',
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Text Blocks:</div>',
          (pi.textBlocks?.length
            ? pi.textBlocks.map(t => kv(t.id, `"${t.text}" (${t.extractionMethod})`)).join('')
            : '<span style="color:#475569;font-size:0.82rem;">None extracted yet</span>'),
        ].join(''))}

        ${section('🤖 VLM Semantic Understanding (PR-05)', [
          kv('Classification', badge((result.classification || 'unknown').toUpperCase(), statusColor), true),
          kv('Provider / Model', `${bi.provenance?.provider || '—'} / ${bi.provenance?.model || '—'}`),
          kv('Confidence', `isPhysics: ${(result.confidence.isPhysics ?? 0).toFixed(2)}, domain: ${(result.confidence.domain ?? 0).toFixed(2)}, subtype: ${(result.confidence.subtype ?? 0).toFixed(2)}`),
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Semantic Roles & Entities:</div>',
          (result.entities?.length
            ? result.entities.map(e => kv(`${e.id} (${e.type})`, `${e.label ? `"${e.label}" ` : ''}[${e.attributes?.precision || 'approximate'}] conf: ${(e.attributes?.confidence ?? 0.0).toFixed(2)}`)).join('')
            : '<span style="color:#475569;font-size:0.82rem;">None identified</span>'),
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Observed Labels (Unverified Evidence):</div>',
          (result.visibleLabels?.length
            ? result.visibleLabels.map(l => kv(l.text, `(role: ${l.semanticRole || 'general'}, conf: ${(l.confidence ?? 0.0).toFixed(2)})`)).join('')
            : '<span style="color:#475569;font-size:0.82rem;">No text/parameter labels observed</span>'),
          (result.candidates?.length
            ? '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Candidate Interpretations:</div>' +
              result.candidates.map(c => kv(`${c.domain || 'unknown'} / ${c.subtype || 'unknown'}`, `conf: ${(c.confidence ?? 0.0).toFixed(2)}`)).join('')
            : ''),
        ].join(''))}

        ${section('📚 BookIR', [
          kv('Status', badge(bi.status || 'UNRESOLVED', statusColor), true),
          kv('Domain', bi.domain ? escapeHtml(bi.domain) : '<span style="color:#475569">null — not identified</span>', true),
          kv('Subtype', bi.subtype ? escapeHtml(bi.subtype) : '<span style="color:#475569">null — not identified</span>', true),
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Entities:</div>',
          entities,
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Parameters:</div>',
          parameters,
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Status Notes:</div>',
          `<div style="color:#94a3b8;font-size:0.8rem;line-height:1.5;">${escapeHtml(bi.statusNotes || '—')}</div>`,
        ].join(''))}

        ${section('⚙️ PhysicsCompiler', [
          kv('Compiler Status', badge(cr.status || 'UNRESOLVED', statusColor), true),
          kv('Scene', cr.scene ? badge('PRESENT', '#22c55e') : badge('null — no simulation fabricated', '#64748b'), true),
          '<div style="margin-top:6px;font-size:0.78rem;color:#64748b;">Issues:</div>',
          issues,
        ].join(''))}
      </div>`;
  }
}
