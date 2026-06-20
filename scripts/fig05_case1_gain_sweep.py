"""Figure 5: 2x2 grid of closed-loop step responses with K = 4.6, 5, 7.67, 7.8.

K = 7.8 is just outside the stability interval (-1, 7.67) --- expect divergence.
"""

from __future__ import annotations

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from _common import configure_mpl, fig_path  # noqa: E402

from foptd_pade.plant import case1_closed_loop_p_only
from foptd_pade.tuning import routh_hurwitz_case1


def _step(K: float, t_final: float):
    sys = case1_closed_loop_p_only(K=K)
    t = np.linspace(0.0, t_final, 4001)
    return ct.step_response(sys, T=t)


def main() -> None:
    configure_mpl()
    _, ku, _ = routh_hurwitz_case1()
    cases = [
        (4.6, 4.0),
        (5.0, 4.0),
        (ku, 4.0),
        (7.8, 100.0),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(9.0, 6.0))
    for ax, (K, t_final) in zip(axes.flat, cases):
        t, y = _step(K, t_final)
        ax.plot(t, y)
        ax.set_title(f"K = {K:.2f}" if K != ku else "K = 7.67")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")
    fig.suptitle("Closed-loop step response of the FOPTD model (Case 1)")
    fig.tight_layout()
    out = fig_path("fig05_case1_gain_sweep.png")
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
