/** Linear RC transients around the existing DC MNA solver.
 * Capacitor voltages are state variables. DC solves at zero and unit state
 * voltages construct dv/dt = A v + b for the actual graph. A matrix exponential
 * advances this affine system without changing the DC solver or its stamps.
 * Parallel capacitors share a state; inconsistent initial voltages are rejected.
 */
import { CircuitCompiler } from './CircuitCompiler.js';
import { CircuitSolver } from './CircuitSolver.js';

function multiply(a, b, n) {
  const out = new Float64Array(n*n);
  for (let i=0;i<n;i++) for (let k=0;k<n;k++) for (let j=0;j<n;j++)
    out[i*n+j] += a[i*n+k]*b[k*n+j];
  return out;
}

// Scaling/squaring with a converged Taylor series on a norm <= 0.5 matrix.
function exponential(matrix, n, dt) {
  let norm=0;
  for (let i=0;i<n;i++) {
    let row=0; for (let j=0;j<n;j++) row+=Math.abs(matrix[i*n+j]*dt);
    norm=Math.max(norm,row);
  }
  if (!Number.isFinite(norm)) throw new Error('RC time step exceeds numeric range.');
  const scale=Math.max(0,Math.ceil(Math.log2(Math.max(1,norm*2))));
  if (scale>50) throw new Error('RC time scales exceed supported numerical range.');
  const a=Float64Array.from(matrix,x=>x*dt/2**scale);
  let term=new Float64Array(n*n), result=new Float64Array(n*n);
  for(let i=0;i<n;i++) term[i*n+i]=result[i*n+i]=1;
  for(let k=1;k<=32;k++) {
    term=multiply(term,a,n); let largest=0;
    for(let i=0;i<term.length;i++) { term[i]/=k;result[i]+=term[i];largest=Math.max(largest,Math.abs(term[i])); }
    if(largest<1e-16) break;
  }
  for(let k=0;k<scale;k++) result=multiply(result,result,n);
  return result;
}

export class CircuitTransientSolver {
  constructor(model) { this.time=0; this.voltages=new Map(); this.load(model); }

  load(model) {
    this.model=model;
    this.groups=[];
    for(const c of model.capacitors || []) {
      if (!(Number.isFinite(c.value) && c.value>0 && Number.isFinite(c.initial_voltage)))
        throw new Error(`Capacitor ${c.id} needs positive capacitance and explicit initial voltage.`);
      let group=this.groups.find(g=>g.nodes.every(n=>c.nodes.includes(n)));
      if(!group) { group={id:c.id,nodes:[...c.nodes],members:[],value:0};this.groups.push(group); }
      const sign=group.nodes[0]===c.nodes[0]?1:-1;
      const voltage=(this.voltages.get(c.id) ?? c.initial_voltage)*sign;
      if(group.members.length && Math.abs(group.voltage-voltage)>1e-8)
        throw new Error('Parallel capacitors have inconsistent initial voltages.');
      group.voltage=voltage;group.value+=c.value;group.members.push({c,sign});
    }
    if(this.groups.length>32) throw new Error('RC runtime supports at most 32 independent capacitor states.');
    const count=this.groups.length;
    const base=this._solve(new Array(count).fill(0));
    this.affine=new Float64Array((count+1)**2);
    for(let i=0;i<count;i++) this.affine[i*(count+1)+count]=base.componentCurrents[this.groups[i].id]/this.groups[i].value;
    for(let j=0;j<count;j++) {
      const unit=new Array(count).fill(0);unit[j]=1;
      const response=this._solve(unit);
      for(let i=0;i<count;i++) this.affine[i*(count+1)+j]=
        (response.componentCurrents[this.groups[i].id]-base.componentCurrents[this.groups[i].id])/this.groups[i].value;
    }
    this._remember();
  }

  _solve(voltages) {
    const scene=this.model.scene;
    const components=scene.circuit.components.filter(c=>c.type!=='capacitor').map(c=>({...c}));
    this.groups.forEach((g,i)=>components.push({id:g.id,type:'voltage_source',nodes:g.nodes,value:voltages[i],unit:'V'}));
    const parameters={...scene.parameters};
    for(const c of this.model.capacitors) delete parameters[c.id];
    const surrogate={...scene,parameters,circuit:{...scene.circuit,components}};
    const state=new CircuitSolver(CircuitCompiler.compile(surrogate)).solveDC();
    if(!state.success) throw new Error(`RC circuit constraints cannot be solved: ${state.error}`);
    return state;
  }

  _remember() {
    for(const g of this.groups) for(const {c,sign} of g.members) this.voltages.set(c.id,g.voltage*sign);
  }

  solveDC() { // Adapter-compatible snapshot; does not advance time.
    const state=this._solve(this.groups.map(g=>g.voltage));
    const capacitorVoltages={}, capacitorCharge={}, capacitorEnergy={};
    for(const g of this.groups) {
      const current=state.componentCurrents[g.id];
      for(const {c,sign} of g.members) {
        const voltage=g.voltage*sign, branch=current*c.value/g.value*sign;
        state.componentVoltages[c.id]=voltage;state.componentCurrents[c.id]=branch;
        state.componentPower[c.id]=voltage*branch;
        capacitorVoltages[c.id]=voltage;capacitorCharge[c.id]=c.value*voltage;
        capacitorEnergy[c.id]=0.5*c.value*voltage*voltage;
      }
    }
    state.totalPower=this.model.resistors.reduce((sum,c)=>sum+state.componentPower[c.id],0);
    return {...state,time:this.time,capacitorVoltages,capacitorCharge,capacitorEnergy};
  }

  step(dt) {
    if(!Number.isFinite(dt) || dt<0) throw new Error('RC time step must be finite and nonnegative.');
    const n=this.groups.length+1, transform=exponential(this.affine,n,dt);
    const initial=[...this.groups.map(g=>g.voltage),1];
    const next=this.groups.map((_,i)=>initial.reduce((sum,v,j)=>sum+transform[i*n+j]*v,0));
    if(next.some(v=>!Number.isFinite(v))) throw new Error('RC solution is non-finite.');
    this.groups.forEach((g,i)=>{g.voltage=next[i];});
    this.time+=dt;this._remember();return this.solveDC();
  }
}
