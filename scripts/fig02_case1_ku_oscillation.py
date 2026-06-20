"""Figure 2: closed-loop step response of Case 1 at K = ku = 7.67.

Marginal-stability test: P-only controller at the Routh-Hurwitz upper bound.
Expected: sustained oscillation of constant amplitude.
"""

from __future__ import annotations

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from _common import configure_mpl, fig_path  # noqa: E402

from foptd_pade.plant import case1_closed_loop_p_only
from foptd_pade.tuning import routh_hurwitz_case1


def main() -> None:
    configure_mpl()
    _, ku, _ = routh_hurwitz_case1()
    sys = case1_closed_loop_p_only(K=ku)
    t = np.linspace(0.0, 5.0, 4001)
    t_out, y = ct.step_response(sys, T=t)

    fig, ax = plt.subplots()
    ax.plot(t_out, y, color="tab:blue")
    ax.axhline(1.0, color="k", lw=0.6, ls="--", alpha=0.5)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Output Response")
    ax.set_title(f"Case 1: sustained oscillation at K = $k_u$ = {ku:.2f}")
    ax.set_xlim(0, 5)
    fig.tight_layout()
    out = fig_path("fig02_case1_ku_oscillation.png")
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
