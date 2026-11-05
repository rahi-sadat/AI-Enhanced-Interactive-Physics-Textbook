"""Explicit, component-owned decisions for missing circuit values."""
from copy import deepcopy

from ai.resolution.units import UnitEngine
from ai.resolution.policies import PolicyRegistry
from ai.resolution.evaluator import ReadinessEvaluator
from shared.schemas.ingestion import ProvenanceRecord


def component_field(parameter):
    return parameter.rsplit('.',1)[-1]


def component_target(book, parameter):
    if book.subtype != "dc_linear" or not parameter.startswith("component.") or component_field(parameter) not in {"value","initial_voltage"}:
        return None
    identity = parameter[len("component."):].rsplit('.',1)[0]
    matches = [c for c in book.parameters.get("components", []) if c.get("id") == identity]
    return matches[0] if len(matches) == 1 else None


def value_spec(component, field="value"):
    if field=="initial_voltage":
        return ("voltage", "V", "policy_uncharged_capacitor") if component["type"]=="capacitor" else None
    if component["type"]=="capacitor":
        return "capacitance", "F", "policy_standard_capacitance"
    if component["type"] in {"voltage_source", "battery", "dc_source"}:
        return "voltage", "V", "policy_standard_dc_voltage"
    if component["type"] in {"resistor", "bulb", "lamp"}:
        return "resistance", "Ω", "policy_standard_dc_resistance"
    return None


def refresh_value_state(book, component):
    """Refresh value-dependent flags without changing measured geometry."""
    for diagnostic in book.provenance.get("grounding_diagnostics", []):
        identity = diagnostic.get("entity_id", diagnostic.get("entityId"))
        if identity == component["id"]:
            diagnostic.setdefault("checks", {})["parameter_value"] = component.get("value") is not None
            complete = all(diagnostic["checks"].values())
            diagnostic["groundingState"] = "grounded" if complete else "unresolved"
            diagnostic["notes"] = "" if complete else "Review " + ", ".join(
                key for key, passed in diagnostic["checks"].items() if not passed)
    for entity in book.entities:
        if entity.id == component["id"] and entity.geometry:
            entity.attributes["grounding_state"] = "grounded" if component.get("value") is not None else "unresolved"


def resolve_component_value(book, decision):
    from ai.resolution.engine import ResolutionResult
    name = decision.parameter_name
    field = component_field(name)
    unit_key = "unit" if field=="value" else field+"_unit"
    provenance_key = field+"_provenance"
    component = component_target(book, name)
    def reject(message):
        return ResolutionResult(success=False, parameter_name=name, error=message)
    if component is None or not value_spec(component,field):
        return reject("Unknown circuit component or unsupported value type.")
    if component.get("verification_status") != "VERIFIED":
        return reject("Verify the component and its connections before choosing a value.")
    dimension, unit, policy_id = value_spec(component,field)
    source = getattr(decision.resolution_source, "value", decision.resolution_source)
    automatic = source == "policy_default" and decision.resolved_by == "auto_policy"
    if not decision.user_accepted and not automatic:
        return reject("Confirm this value before applying it.")
    value = decision.resolved_value if decision.resolved_value is not None else decision.original_entered_value
    entered_unit = decision.canonical_unit or decision.original_unit
    if source == "policy_default":
        if component.get(field) is not None:
            return reject("Defaults apply only to missing values; this component already has a value.")
        if decision.policy_id != policy_id:
            return reject("This default does not apply to this component.")
        policy = PolicyRegistry.get_policy(policy_id)
        value, entered_unit = policy.value, policy.unit
        decision.policy_version = policy.version
    elif source not in {"user_supplied", "user_corrected", "user_confirmed"}:
        return reject("A user decision is required for a missing circuit value.")
    parsed = UnitEngine.parse_quantity(value, entered_unit, dimension)
    if not parsed.success:
        return reject(parsed.error)
    if dimension in {"resistance","capacitance"} and parsed.canonical_value <= 0:
        return reject(f"{dimension.capitalize()} must be greater than zero.")
    previous = book.resolutions.get(name)
    decision.superseded_value = (previous.get("supersededValue", previous.get("superseded_value"))
                                 if previous else {k:deepcopy(component[k]) for k in
                                 (field, unit_key, provenance_key) if k in component})
    decision.resolved_value = decision.value = parsed.canonical_value
    decision.canonical_unit = decision.unit = parsed.canonical_unit
    component.update({field:parsed.canonical_value, unit_key:parsed.canonical_unit,
                     provenance_key:{"source":"auto_policy" if automatic else source, "policy_id":decision.policy_id,
                                       "policy_version":decision.policy_version,
                                       "user_accepted":decision.user_accepted, "evidence_refs":[]}})
    book.resolutions[name] = decision.model_dump()
    book.parameter_provenance[name] = ProvenanceRecord(
        source="auto_policy" if automatic else source, user_accepted=decision.user_accepted,
        policy_id=decision.policy_id, policy_version=decision.policy_version,
        confidence=0.8 if automatic else 1.0,
        notes="Assumed for simulation; source image evidence is unchanged." if automatic
              else "Explicit component value; source image evidence is unchanged.")
    refresh_value_state(book, component)
    readiness = ReadinessEvaluator.evaluate(book, mutate_status=True)
    return ResolutionResult(success=True, parameter_name=name, resolved_value=parsed.canonical_value,
                            canonical_unit=parsed.canonical_unit, resolution=decision,
                            readiness_report=readiness)


def remove_component_value(book, name):
    component = component_target(book, name)
    decision = book.resolutions.pop(name, None)
    if component is not None and decision:
        previous = decision.get("supersededValue", decision.get("superseded_value")) or {}
        field=component_field(name)
        for key in (field, "unit" if field=="value" else field+"_unit", field+"_provenance"):
            component.pop(key, None)
        component.update(deepcopy(previous))
        book.parameter_provenance.pop(name, None)
        refresh_value_state(book, component)
    return ReadinessEvaluator.evaluate(book, mutate_status=True)
