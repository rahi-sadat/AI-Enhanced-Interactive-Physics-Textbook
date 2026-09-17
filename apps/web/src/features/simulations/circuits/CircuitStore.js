/**
 * circuits/CircuitStore.js
 * Centralized multi-layer state manager for the circuit domain.
 * Strictly separates:
 * 1. CircuitScene (Perception / raw backend JSON)
 * 2. CircuitModel (Compiled electrical topology & polyline metrics)
 * 3. ElectricalState (Solved numbers: voltages, currents, power)
 * 4. UIState (Selection, active mode, probes, animation, provenance overrides)
 */

export class CircuitStore {
  constructor(scene, model, electricalState) {
    this.scene = scene;
    this.model = model;
    this.electricalState = electricalState;

    // UI & Interaction State
    this.uiState = {
      mode: 'inspect', // 'inspect' | 'edit' | 'voltage-probe' | 'current-probe' | 'kcl' | 'kvl' | 'debug'
      selectedComponentId: null,
      hoveredComponentId: null,
      selectedNodeId: null,
      hoveredNodeId: null,
      activeLoopId: null,
      animationEnabled: true,
      showNodeVoltages: true,
      showEquipotential: true,
      debugOverlay: false,
      voltageProbe: { active: false, leadRed: null, leadBlack: null, reading: null },
      currentProbe: { active: false, targetBranch: null, reading: null }
    };

    // Parameter Overrides with Provenance Tracking
    // Map<componentId, { originalValue, overrideValue, source, paramKey }>
    this.overrides = new Map();

    // Command History for Undo/Redo
    this.history = [];
    this.historyIndex = -1;

    // Event listeners
    this._listeners = new Set();
  }

  subscribe(listener) {
    this._listeners.add(listener);
    return () => this._listeners.delete(listener);
  }

  notify(changeType, payload = {}) {
    for (const listener of this._listeners) {
      listener(changeType, payload, this);
    }
  }

  setMode(mode) {
    if (this.uiState.mode === mode) return;
    this.uiState.mode = mode;
    this.notify('MODE_CHANGED', { mode });
  }

  setSelectedComponent(componentId) {
    this.uiState.selectedComponentId = componentId;
    this.notify('SELECTION_CHANGED', { componentId });
  }

  setHoveredComponent(componentId) {
    if (this.uiState.hoveredComponentId === componentId) return;
    this.uiState.hoveredComponentId = componentId;
    this.notify('HOVER_CHANGED', { componentId });
  }

  setSelectedNode(nodeId) {
    this.uiState.selectedNodeId = nodeId;
    this.notify('NODE_SELECTED', { nodeId });
  }

  setHoveredNode(nodeId) {
    if (this.uiState.hoveredNodeId === nodeId) return;
    this.uiState.hoveredNodeId = nodeId;
    this.notify('NODE_HOVER_CHANGED', { nodeId });
  }

  toggleAnimation() {
    this.uiState.animationEnabled = !this.uiState.animationEnabled;
    this.notify('ANIMATION_TOGGLED', { enabled: this.uiState.animationEnabled });
  }

  toggleDebug() {
    this.uiState.debugOverlay = !this.uiState.debugOverlay;
    this.notify('DEBUG_TOGGLED', { enabled: this.uiState.debugOverlay });
  }

  /**
   * Set a component parameter override with provenance preservation.
   */
  setParameter(componentId, paramKey, value) {
    const comp = this.model.componentById.get(componentId);
    if (!comp) return;

    const original = this.overrides.get(componentId)?.originalValue ?? comp[paramKey] ?? comp.value;
    const previous = comp[paramKey] ?? comp.value;

    this.overrides.set(componentId, {
      componentId,
      paramKey,
      originalValue: original,
      overrideValue: value,
      source: 'student'
    });

    comp[paramKey] = value;
    comp.value = value;

    // Push undo action
    this._pushHistory({
      type: 'SET_PARAMETER',
      componentId,
      paramKey,
      previous,
      next: value
    });

    this.notify('PARAMETER_CHANGED', { componentId, paramKey, previous, value, original });
  }

  /**
   * Restore a component to its original textbook value.
   */
  restoreTextbookValue(componentId) {
    const override = this.overrides.get(componentId);
    if (!override) return;

    const { paramKey, originalValue } = override;
    this.setParameter(componentId, paramKey, originalValue);
    this.overrides.delete(componentId);
    this.notify('PARAMETER_RESTORED', { componentId, paramKey, value: originalValue });
  }

  /**
   * Toggle a switch state between 'open' and 'closed'.
   */
  toggleSwitch(switchId) {
    const compInModel = this.model?.componentById?.get(switchId);
    const compInScene = this.scene?.circuit?.components?.find(c => c.id === switchId);

    const currentState = compInModel?.state || compInScene?.state || 'closed';
    const newState = (currentState === 'open') ? 'closed' : 'open';

    if (compInModel) compInModel.state = newState;
    if (compInScene) compInScene.state = newState;

    this.notify('SWITCH_TOGGLED', { switchId, state: newState });
    return newState;
  }

  /**
   * Reset all student modifications back to original textbook state.
   */
  resetToTextbook() {
    for (const [cid, ov] of this.overrides.entries()) {
      const comp = this.model.componentById.get(cid);
      if (comp) {
        comp[ov.paramKey] = ov.originalValue;
        comp.value = ov.originalValue;
      }
    }
    this.overrides.clear();
    this.history = [];
    this.historyIndex = -1;
    this.notify('RESET_ALL', {});
  }

  _pushHistory(action) {
    this.history = this.history.slice(0, this.historyIndex + 1);
    this.history.push(action);
    this.historyIndex++;
  }

  undo() {
    if (this.historyIndex < 0) return;
    const action = this.history[this.historyIndex];
    this.historyIndex--;

    if (action.type === 'SET_PARAMETER') {
      const comp = this.model.componentById.get(action.componentId);
      if (comp) {
        comp[action.paramKey] = action.previous;
        comp.value = action.previous;
        this.notify('PARAMETER_CHANGED', {
          componentId: action.componentId,
          paramKey: action.paramKey,
          value: action.previous
        });
      }
    }
  }

  redo() {
    if (this.historyIndex >= this.history.length - 1) return;
    this.historyIndex++;
    const action = this.history[this.historyIndex];

    if (action.type === 'SET_PARAMETER') {
      const comp = this.model.componentById.get(action.componentId);
      if (comp) {
        comp[action.paramKey] = action.next;
        comp.value = action.next;
        this.notify('PARAMETER_CHANGED', {
          componentId: action.componentId,
          paramKey: action.paramKey,
          value: action.next
        });
      }
    }
  }
}
