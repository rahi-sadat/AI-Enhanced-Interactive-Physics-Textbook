/** Source-space inspection only: no runtime, currents, defaults or playback. */
export function circuitInspection(book, imageUrl, sourceAsset = {}) {
  const width = sourceAsset.width_px || book?.geometry?.width;
  const height = sourceAsset.height_px || book?.geometry?.height;
  const components = book?.parameters?.components || [];
  const boxes = (book?.entities || []).map(entity => ({id:entity.id,type:entity.type,
    box:entity.attributes?.circuitV2BBox || null,
    verified:components.some(c => c.id===entity.id && c.verification_status==='VERIFIED')}));
  return {imageUrl,width,height,boxes,components,
    blockers:[...(book?.reviewIssues || []),...(book?.provenance?.circuit_geometry_issues || [])]};
}

export function renderCircuitInspection(host, inspection) {
  const section=document.createElement('section');
  const title=document.createElement('h3');title.textContent='Inspect the source circuit';section.appendChild(title);
  // One SVG viewBox holds both source image and measured boxes. They share the
  // same aspect-preserving transform at every browser size and device scale.
  if (inspection.width && inspection.height && inspection.imageUrl) {
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');svg.setAttribute('viewBox',`0 0 ${inspection.width} ${inspection.height}`);
    svg.setAttribute('aria-label','Original source with component proposals');svg.style.width='100%';svg.style.maxHeight='420px';
    const image=document.createElementNS(ns,'image');image.setAttribute('href',inspection.imageUrl);
    image.setAttribute('width',inspection.width);image.setAttribute('height',inspection.height);svg.appendChild(image);
    for (const item of inspection.boxes) {
      const b=item.box;if (!b) continue;
      const rect=document.createElementNS(ns,'rect');
      for (const key of ['x','y','width','height']) rect.setAttribute(key,b[key]);
      rect.setAttribute('fill','none');rect.setAttribute('stroke',item.verified?'#22c55e':'#f59e0b');
      rect.setAttribute('stroke-width',Math.max(1,inspection.width/600));
      const label=document.createElementNS(ns,'title');label.textContent=`${item.id}: ${item.type}; ${item.verified?'verified geometry':'proposal requires review'}`;
      rect.appendChild(label);svg.appendChild(rect);
    }
    section.appendChild(svg);
  }
  const list=document.createElement('ol');
  for (const issue of inspection.blockers) {
    const item=document.createElement('li');item.textContent=`${issue.code || 'Reconstruction'}: ${issue.message || issue.notes || ''}`;list.appendChild(item);
  }
  section.appendChild(list);
  const help=document.createElement('p');help.textContent='Inspect the highlighted proposals and correct component values below. For missing symbols or wires, close this dialog and upload a clearer complete crop. Geometry stays in review until source pixels support it.';
  section.appendChild(help);host.appendChild(section);
}
