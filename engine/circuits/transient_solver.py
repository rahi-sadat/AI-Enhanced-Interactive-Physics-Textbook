"""backend/circuits/solver/transient_solver.py

Time-domain transient simulation for educational RC circuits.
Provides closed-form analytical solutions for standard series RC charging and discharging,
matching the project's analytical precision philosophy (like RK4 pendulum and analytical projectile).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class TransientCurve:
    time_s: list[float]
    vc_v: list[float]
    current_a: list[float]
    tau_s: float
    vs_v: float
    r_ohm: float
    c_f: float
    mode: str  # "charging" or "discharging"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tau_s": round(self.tau_s, 6),
            "time_constant_s": round(self.tau_s, 6),
            "mode": self.mode,
            "vs_v": self.vs_v,
            "r_ohm": self.r_ohm,
            "c_f": self.c_f,
            "time_s": [round(t, 6) for t in self.time_s],
            "vc_v": [round(v, 4) for v in self.vc_v],
            "current_a": [round(i, 6) for i in self.current_a],
        }


def solve_rc_transient(
    vs_v: float,
    r_ohm: float,
    c_f: float,
    mode: str = "charging",
    v0_v: float = 0.0,
    steps: int = 100,
) -> TransientCurve:
    """Computes exact analytical time-domain trajectory for a series RC circuit.
    
    Charging:
      V_c(t) = V_s * (1 - exp(-t / tau))
      I(t)   = (V_s / R) * exp(-t / tau)
      
    Discharging:
      V_c(t) = V_0 * exp(-t / tau)
      I(t)   = -(V_0 / R) * exp(-t / tau)
    """
    tau = r_ohm * c_f
    if tau <= 0:
        tau = 1e-6

    # Simulate across 5 time constants (99.3% settled)
    t_max = 5.0 * tau
    dt = t_max / max(1, steps - 1)

    time_pts: list[float] = []
    vc_pts: list[float] = []
    i_pts: list[float] = []

    for i in range(steps):
        t = i * dt
        time_pts.append(t)
        exp_factor = math.exp(-t / tau)

        if mode == "charging":
            vc = vs_v * (1.0 - exp_factor)
            cur = (vs_v / r_ohm) * exp_factor
        else:  # discharging
            v_init = v0_v if v0_v != 0.0 else vs_v
            vc = v_init * exp_factor
            cur = -(v_init / r_ohm) * exp_factor

        vc_pts.append(vc)
        i_pts.append(cur)

    return TransientCurve(
        time_s=time_pts,
        vc_v=vc_pts,
        current_a=i_pts,
        tau_s=tau,
        vs_v=vs_v,
        r_ohm=r_ohm,
        c_f=c_f,
        mode=mode,
    )
