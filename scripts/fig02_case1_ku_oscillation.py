"""Figure 2: closed-loop step response of Case 1 at K = ku = 7.67.

Marginal-stability test: P-only controller at the Routh-Hurwitz upper bound.
Expected: sustained oscillation of constant amplitude.
"""

from __future__ import annotations

import control as ct
import numpy as np

from _common import configure_mpl, new_figure, save_figure  # noqa: E402

from foptd_pade.plant import case1_closed_loop_p_only
from foptd_pade.tuning import routh_hurwitz_case1


def main() -> None:
    configure_mpl()
    _, ku, _ = routh_hurwitz_case1()
    sys = case1_closed_loop_p_only(K=ku)
    t = np.linspace(0.0, 5.0, 4001)
    t_out, y = ct.step_response(sys, T=t)

    fig, ax = new_figure(figsize=(7.0, 4.5), top=0.97, bottom=0.16)
    ax.plot(t_out, y, color="tab:blue")
    ax.axhline(1.0, color="k", lw=0.6, ls="--", alpha=0.5)
    ax.grid(True)
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Output Response")
    ax.set_xlim(0, 5)
    png, pdf = save_figure(fig, "fig02_case1_ku_oscillation")
    print(f"wrote {png}\nwrote {pdf}")


if __name__ == "__main__":
    main()
