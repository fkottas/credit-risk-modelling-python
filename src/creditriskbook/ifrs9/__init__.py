"""Transparent IFRS 9 teaching components with explicit policy inputs.

The package keeps staging, term structures, scenarios, discounting, overlays,
and reconciliation separate.  That separation is intentional: institutions
must be able to identify which result comes from a model and which comes from
an approved accounting or risk policy.
"""

from .curves import (
    constant_hazard_curve,
    cumulative_to_marginal,
    hazard_to_marginal,
    marginal_to_cumulative,
    marginal_to_hazard,
    scale_hazard,
)
from .engine import ECLConfig, ECLResult, Scenario, calculate_ecl
from .overlays import apply_overlay, reconcile_ecl
from .provision_matrix import build_provision_matrix
from .staging import StagingPolicy, assign_stages

__all__ = [
    "ECLConfig",
    "ECLResult",
    "Scenario",
    "StagingPolicy",
    "apply_overlay",
    "assign_stages",
    "build_provision_matrix",
    "calculate_ecl",
    "constant_hazard_curve",
    "cumulative_to_marginal",
    "hazard_to_marginal",
    "marginal_to_cumulative",
    "marginal_to_hazard",
    "reconcile_ecl",
    "scale_hazard",
]
