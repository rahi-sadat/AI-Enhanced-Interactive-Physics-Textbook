/** Cut-set currents on verified source edges. Cyclic/unsupported flow stays null. */
export function measuredWireFlows(circuit, branchCurrents) {
  const wires=circuit?.wires || [];
  if (!wires.some(w=>w.verification_status==='VERIFIED' || w.provenance?.source==='diagram_measurement')) return null;
  const unknown=()=>new Map(wires.map(w=>[w.id,{current_A:null,direction:'none'}]));
  const edges=new Map(),coordinates=new Map(),injections=new Map();
  const add=(v,n)=>injections.set(v,(injections.get(v)||0)+n);
  for(const w of wires) {
    if(w.verification_status!=='VERIFIED' || !Array.isArray(w.ends) || w.ends.length!==2 || !w.points?.length) return unknown();
    const ends=w.ends.map((end,i)=>end?`junction:${end}`:`${w.id}:${i}`);
    for(let i=0;i<2;i++) {
      const point=w.points[i===0?0:w.points.length-1];
      if(coordinates.has(ends[i]) && JSON.stringify(coordinates.get(ends[i]))!==JSON.stringify(point))return unknown();
      coordinates.set(ends[i],point);
    }
    edges.set(w.id,ends);
  }
  for(const c of circuit.components || []) {
    const current=branchCurrents?.[c.id];if(!Number.isFinite(current) || c.terminals?.length!==2)return unknown();
    for(let i=0;i<2;i++) {
      const t=c.terminals[i],edge=edges.get(t.wire_id);
      if(!edge || ![0,-1].includes(t.wire_end))return unknown();
      add(edge[t.wire_end===0?0:1],(i===0?1:-1)*current);
    }
  }
  const reachable=(start,excluded)=>{
    const seen=new Set([start]),queue=[start];
    while(queue.length) {
      const at=queue.shift();
      for(const [id,[a,b]] of edges) {
        if(id===excluded)continue;
        const next=a===at?b:b===at?a:null;
        if(next!==null && !seen.has(next)){seen.add(next);queue.push(next);}
      }
    }
    return seen;
  };
  // Invalid terminal injections cannot authorize an animation even if MNA has
  // separately solved a client-tampered collapsed graph.
  const scale=Math.max(1,...Object.values(branchCurrents || {}).map(Math.abs));
  for(const vertex of coordinates.keys()) {
    const region=reachable(vertex,null);
    if(Math.abs([...region].reduce((sum,v)=>sum+(injections.get(v)||0),0))>1e-9*scale)return unknown();
  }
  return new Map([...edges].map(([id,[a,b]])=>{
    const cut=reachable(a,id);
    const current=cut.has(b)?null:-[...cut].reduce((sum,v)=>sum+(injections.get(v)||0),0);
    return [id,{current_A:current===null?null:Math.abs(current),direction:current===null || Math.abs(current)<1e-9?'none':current>0?'forward':'backward'}];
  }));
}
