"""Tools for the synthetic FlowAgent — a small engineering-assistant surface.

These mirror the *shape* of Synera tool calls (typed inputs, structured
outputs, real failure modes) without exposing any real product code. The numbers
are synthetic but internally consistent so that trajectories can be checked for
correctness.
"""

from __future__ import annotations

import hashlib
from typing import Any, Callable


class ToolError(Exception):
    """Raised for recoverable, domain-level tool failures (unknown material,
    invalid geometry, ...). The agent is expected to handle these gracefully."""


# Synthetic material database. density in g/cm^3, yield strength in MPa.
_MATERIALS: dict[str, dict[str, float]] = {
    "aluminum": {"density_g_cm3": 2.70, "yield_strength_mpa": 95.0},
    "steel": {"density_g_cm3": 7.85, "yield_strength_mpa": 250.0},
    "titanium": {"density_g_cm3": 4.43, "yield_strength_mpa": 880.0},
    "abs_plastic": {"density_g_cm3": 1.05, "yield_strength_mpa": 40.0},
}


def lookup_material(name: str) -> dict[str, float]:
    """Return density and yield strength for a known material."""
    key = str(name).strip().lower()
    if key not in _MATERIALS:
        raise ToolError(f"unknown material {name!r}; known: {sorted(_MATERIALS)}")
    return dict(_MATERIALS[key])


def compute_mass(volume_cm3: float, density_g_cm3: float) -> float:
    """Mass in grams = volume (cm^3) * density (g/cm^3)."""
    return round(float(volume_cm3) * float(density_g_cm3), 3)


def run_simulation(load_n: float, cross_section_mm2: float) -> dict[str, float]:
    """Axial stress in MPa = load (N) / cross-section (mm^2). 1 N/mm^2 == 1 MPa."""
    if float(cross_section_mm2) <= 0:
        raise ToolError("cross_section_mm2 must be > 0")
    stress = float(load_n) / float(cross_section_mm2)
    return {"max_stress_mpa": round(stress, 3)}


def compute_safety_factor(yield_strength_mpa: float, max_stress_mpa: float) -> float:
    """Safety factor = yield strength / max stress (both MPa)."""
    if float(max_stress_mpa) <= 0:
        raise ToolError("max_stress_mpa must be > 0")
    return round(float(yield_strength_mpa) / float(max_stress_mpa), 3)


def unit_convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert between a small set of engineering units."""
    factors: dict[tuple[str, str], float] = {
        ("m3", "cm3"): 1e6,
        ("cm3", "m3"): 1e-6,
        ("mm2", "cm2"): 1e-2,
        ("cm2", "mm2"): 1e2,
        ("kn", "n"): 1e3,
        ("n", "kn"): 1e-3,
    }
    pair = (str(from_unit).strip().lower(), str(to_unit).strip().lower())
    if pair not in factors:
        raise ToolError(f"unsupported conversion {from_unit}->{to_unit}")
    return round(float(value) * factors[pair], 6)


def write_report(summary: str) -> dict[str, str]:
    """Persist a short report and return its id (deterministic for repeatability)."""
    digest = hashlib.sha1(str(summary).encode("utf-8")).hexdigest()[:6].upper()
    return {"report_id": f"RPT-{digest}"}


TOOLS: dict[str, Callable[..., Any]] = {
    "lookup_material": lookup_material,
    "compute_mass": compute_mass,
    "run_simulation": run_simulation,
    "compute_safety_factor": compute_safety_factor,
    "unit_convert": unit_convert,
    "write_report": write_report,
}
