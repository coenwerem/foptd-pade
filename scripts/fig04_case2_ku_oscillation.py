"""Figure 4: closed-loop step response of Case 2 at K = ku = 5.8902.

Case 2 uses the *true-delay* FOPTD plant (simulated via high-order Pade in Python).
Expected: sustained oscillation; some smoothing relative to MATLAB's DDE solver.
"""

from __future__ import annotations

import control as ct
import numpy as np

from _common import configure_mpl, new_figure, save_figure  # noqa: E402

from foptd_pade.plant import true_plant_high_order_pade
from foptd_pade.tuning import nyquist_case2_ku_tu


def main() -> None:
    configure_mpl()
    _, _, ku, _ = nyquist_case2_ku_tu(pade_order=30)
    G = true_plant_high_order_pade(order=12)
    CL = ct.feedback(ku * G, 1)

    t = np.linspace(0.0, 10.0, 8001)
    t_out, y = ct.step_response(CL, T=t)

    fig, ax = new_figure(figsize=(7.0, 4.5), top=0.97, bottom=0.16)
    ax.plot(t_out, y, color="tab:red")
    ax.axhline(1.0, color="k", lw=0.6, ls="--", alpha=0.5)
    ax.grid(True)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Output Response")
    ax.set_xlim(0, 10)
    png, pdf = save_figure(fig, "fig04_case2_ku_oscillation")
    print(f"wrote {png}\nwrote {pdf}")


if __name__ == "__main__":
    main()
