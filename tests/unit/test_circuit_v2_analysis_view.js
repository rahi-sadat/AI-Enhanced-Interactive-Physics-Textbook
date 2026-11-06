import assert from 'node:assert/strict';
import { analysisOutput, faultInputs, parseAnalysisResponse } from '../../apps/web/src/features/circuit-v2/analysisOutput.js';

const graph = {components:[{id:'r',geometry:{orientation:'vertical'}}],wires:[
  {id:'wire',points:[[2,3],[2,9],[8,9]]},{id:'cycle',points:[[3,4],[7,8]]}]};
const before = structuredClone(graph);
for (const status of ['IDEAL_REJECTED','QUALITATIVE_FAULT','NEEDS_REVIEW']) {
  const result = analysisOutput({status,graph,wire_currents_a:{wire:123},electrical_state:{components:{}},
    validation:{valid:true},fault_path_id:'wire'});
  assert.equal(result.telemetry,null);
  assert.equal(result.geometry.wires[0].current_A,null);
  assert.equal(result.geometry.wires[0].direction,'none');
  assert.equal(result.geometry.wires[0].fault,true);
}
const state = {components:{r:{current_a:-1}}};
const result = analysisOutput({status:'NON_IDEAL_SOLVED',graph,electrical_state:state,validation:{valid:true},
  wire_currents_a:{wire:-2,cycle:null},fault_path_id:'wire'});
assert.deepEqual(result.geometry.wires[0].points,graph.wires[0].points);
assert.equal(result.geometry.wires[0].direction,'backward');
assert.equal(result.geometry.wires[0].current_A,-2);
assert.equal(result.geometry.wires[1].current_A,null);
assert.deepEqual(result.telemetry,state);
assert.deepEqual(graph,before);
assert.deepEqual(faultInputs('',''),{source_internal_resistance_ohm:null,short_path_resistance_ohm:null});
assert.deepEqual(faultInputs('0','2'),{source_internal_resistance_ohm:0,short_path_resistance_ohm:2});
for (const [internal,path] of [['-1','2'],['1','0'],['NaN','2'],['1','Infinity']]) assert.throws(() => faultInputs(internal,path));
console.log('Circuit V2 view: assertions passed');
assert.throws(()=>parseAnalysisResponse('',500),/backend may be offline or restarting/);
assert.throws(()=>parseAnalysisResponse('<html>proxy error</html>',502),/HTTP 502/);
assert.deepEqual(parseAnalysisResponse('{"status":"NEEDS_REVIEW"}',200),{status:'NEEDS_REVIEW'});
