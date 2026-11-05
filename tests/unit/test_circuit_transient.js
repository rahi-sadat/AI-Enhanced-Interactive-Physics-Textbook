import assert from 'node:assert/strict';
import { CircuitCompiler } from '../../engine/circuits/CircuitCompiler.js';
import { CircuitTransientSolver } from '../../engine/circuits/CircuitTransientSolver.js';
import { CircuitAdapter } from '../../engine/circuits/CircuitAdapter.js';
const close=(a,b,tol=1e-8)=>assert.ok(Math.abs(a-b)<tol,`${a} != ${b}`);
const scene=(extra=[])=>({domain:'circuits',subtype:'dc_linear',parameters:{
  V:{value:10,unit:'V',editable:true,min:0,max:20},R:{value:1000,unit:'Ω',editable:true,min:1,max:10000},
  C:{value:.001,unit:'F',editable:true,min:1e-9,max:1}},circuit:{reference_node:'g',nodes:['g','a','b'],wires:[],components:[
  {id:'V',type:'voltage_source',nodes:['a','g'],value:10,unit:'V'},
  {id:'R',type:'resistor',nodes:['a','b'],value:1000,unit:'Ω'},
  {id:'C',type:'capacitor',nodes:['b','g'],value:.001,unit:'F',initial_voltage:0},...extra]}});
const s=scene(),solver=new CircuitTransientSolver(CircuitCompiler.compile(s));
close(solver.solveDC().capacitorVoltages.C,0);
close(solver.solveDC().componentCurrents.R,.01);
let state=solver.step(1);
close(state.capacitorVoltages.C,10*(1-Math.exp(-1)));
close(state.componentCurrents.R,.01*Math.exp(-1));
close(state.capacitorEnergy.C,.5*.001*state.capacitorVoltages.C**2);
// Changing source voltage must preserve stored capacitor voltage and allow discharge.
s.parameters.V.value=0;solver.load(CircuitCompiler.compile(s));
const before=state.capacitorVoltages.C;
state=solver.step(1);close(state.capacitorVoltages.C,before*Math.exp(-1));
assert.ok(state.componentCurrents.R<0);
// Parallel capacitors, including reversed terminal ordering, share voltage and split current by C.
const p=new CircuitTransientSolver(CircuitCompiler.compile(scene([
 {id:'C2',type:'capacitor',nodes:['g','b'],value:.002,unit:'F',initial_voltage:0}])));
state=p.step(3);close(state.capacitorVoltages.C,10*(1-Math.exp(-1)));
close(state.capacitorVoltages.C2,-state.capacitorVoltages.C);
close(state.componentCurrents.C2,-2*state.componentCurrents.C);
// Independent RC branches are not a single hardcoded circuit formula.
const multi=scene();multi.circuit.nodes.push('d');multi.circuit.components.push(
 {id:'R2',type:'resistor',nodes:['a','d'],value:2000,unit:'Ω'},
 {id:'C2',type:'capacitor',nodes:['d','g'],value:.002,unit:'F',initial_voltage:5});
const m=new CircuitTransientSolver(CircuitCompiler.compile(multi));state=m.step(2);
close(state.capacitorVoltages.C,10*(1-Math.exp(-2)));
close(state.capacitorVoltages.C2,10-5*Math.exp(-.5));
// Small and large steps agree; stable long-time limit.
const small=new CircuitTransientSolver(CircuitCompiler.compile(scene()));
for(let i=0;i<100;i++) state=small.step(.01);
close(state.capacitorVoltages.C,10*(1-Math.exp(-1)));
close(small.step(100).capacitorVoltages.C,10,1e-7);
assert.throws(()=>small.step(NaN));
// Actual adapter lifecycle: pause, editing, reset and evidence immutability.
const original=scene(), evidence=JSON.stringify(original), adapter=new CircuitAdapter();
await adapter.initialize(original);adapter.step(1);close(adapter.getState().capacitorVoltages.C,0);
adapter.start();adapter.step(1);close(adapter.getState().capacitorVoltages.C,10*(1-Math.exp(-1)));
adapter.updateParameter('V',0);adapter.step(1);assert.ok(adapter.getState().capacitorVoltages.C<4);
adapter.reset();close(adapter.getState().capacitorVoltages.C,0);assert.equal(adapter.getState().running,false);
assert.equal(JSON.stringify(original),evidence);
const series=scene();series.circuit.nodes.push('d');series.circuit.components.find(c=>c.id==='C').nodes=['b','d'];
series.circuit.components.push({id:'C2',type:'capacitor',nodes:['d','g'],value:.002,unit:'F',initial_voltage:0});
state=new CircuitTransientSolver(CircuitCompiler.compile(series)).step(1);
close(state.capacitorVoltages.C,20/3*(1-Math.exp(-1.5)));
close(state.capacitorVoltages.C2,10/3*(1-Math.exp(-1.5)));
const discharge=scene();discharge.circuit.nodes=['g','b'];
discharge.circuit.components=discharge.circuit.components.filter(c=>c.id!=='V');
discharge.circuit.components.find(c=>c.id==='R').nodes=['b','g'];
discharge.circuit.components.find(c=>c.id==='C').initial_voltage=5;
state=new CircuitTransientSolver(CircuitCompiler.compile(discharge)).step(1);
close(state.capacitorVoltages.C,5*Math.exp(-1));
const switched=scene();switched.circuit.nodes.push('s');
switched.circuit.components.find(c=>c.id==='R').nodes=['s','b'];
switched.circuit.components.push({id:'S',type:'switch',nodes:['a','s'],state:'closed'});
const sw=new CircuitTransientSolver(CircuitCompiler.compile(switched));
const charged=sw.step(1).capacitorVoltages.C;
switched.circuit.components.find(c=>c.id==='S').state='open';sw.load(CircuitCompiler.compile(switched));
close(sw.step(2).capacitorVoltages.C,charged);
console.log('RC transient tests passed: analytic charge/discharge, parallel and independent branches, convergence, lifecycle.');
