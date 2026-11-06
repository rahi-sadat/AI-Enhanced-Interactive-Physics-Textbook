import assert from 'node:assert/strict';
import { measuredWireFlows } from '../../engine/circuits/MeasuredWireFlow.js';
import { circuitInspection } from '../../apps/web/src/features/circuit-v2/evidenceInspection.js';
const wire=(id,a,b)=>({id,ends:[a,b],points:[[a,0],[b,0]],verification_status:'VERIFIED'});
const terminal=(wire_id,wire_end)=>({wire_id,wire_end});
const circuit={wires:[wire('supply',1,2),wire('r1',2,3),wire('r2',2,4),wire('return',5,6),wire('n1',7,6),wire('n2',8,6)],
  components:[{id:'V',terminals:[terminal('supply',0),terminal('return',0)]},
    {id:'R1',terminals:[terminal('r1',-1),terminal('n1',0)]},{id:'R2',terminals:[terminal('r2',-1),terminal('n2',0)]}]};
const before=structuredClone(circuit),currents={V:-3,R1:2,R2:1};
const flows=measuredWireFlows(circuit,currents);
assert.deepEqual(flows.get('supply'),{current_A:3,direction:'forward'});
assert.deepEqual(flows.get('r1'),{current_A:2,direction:'forward'});
assert.deepEqual(flows.get('r2'),{current_A:1,direction:'forward'});
assert.deepEqual(flows.get('return'),{current_A:3,direction:'backward'});
assert.deepEqual(circuit,before);
circuit.wires.push(wire('cycle',2,3));
assert.deepEqual(measuredWireFlows(circuit,currents).get('r1'),{current_A:null,direction:'none'});
assert.equal(measuredWireFlows(circuit,{...currents,V:-4}).get('supply').current_A,null);
assert.equal(measuredWireFlows({wires:[{id:'legacy'}]},{}),null);
const inspection=circuitInspection({geometry:{width:100,height:60},entities:[{id:'R',type:'resistor',
  attributes:{circuitV2BBox:{x:1,y:2,width:3,height:4}}}],reviewIssues:[{code:'FIRST'},{code:'SECOND'}]},'/source.png');
assert.equal(inspection.width,100);assert.equal(inspection.boxes[0].verified,false);
assert.deepEqual(inspection.blockers.map(i=>i.code),['FIRST','SECOND']);
console.log('Measured wire flow and source inspection: passed');
