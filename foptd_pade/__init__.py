"""Python reproduction of Enwerem & Okoro (2023), arXiv:2210.08187.

FOPTD plant: G(s) = e^(-theta*s) / (tau*s + 1), with theta=0.3 s, tau=1.0 s.
"""

from .plant import (
    THETA,
    TAU,
    pade_plant_tf,
    true_plant_high_order_pade,
    case1_closed_loop_p_only,
    case1_closed_loop_pid,
)
from .tuning import (
    routh_hurwitz_case1,
    nyquist_case2_ku_tu,
    ziegler_nichols_pid,
    imc_pi,
    simc_pi,
)
from .metrics import step_metrics

__all__ = [
    "THETA",
    "TAU",
    "pade_plant_tf",
    "true_plant_high_order_pade",
    "case1_closed_loop_p_only",
    "case1_closed_loop_pid",
    "routh_hurwitz_case1",
    "nyquist_case2_ku_tu",
    "ziegler_nichols_pid",
    "imc_pi",
    "simc_pi",
    "step_metrics",
]
