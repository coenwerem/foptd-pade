"""Figure 7: Z-N+Pade vs IMC-PI vs SIMC-PI (tight) vs SIMC-PI (smooth).

IMC and SIMC controllers are applied to the *true-delay* FOPTD plant (numerical proxy
via high-order Pade). The Z-N+Pade controller is applied to its design plant --- the
1/1-Pade-approximated FOPTD --- as in the paper's Eq. (8).
"""

from __future__ import annotations

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from _common import configure_mpl, fig_path  # noqa: E402

from foptd_pade.plant import case1_closed_loop_pid, true_plant_pi_closed_loop
from foptd_pade.tuning import (
    imc_pi,
    routh_hurwitz_case1,
    simc_pi,
    ziegler_nichols_pid,
)


def main() -> None:
    configure_mpl()
    t = np.linspace(0.0, 10.0, 8001)

    # Z-N with Pade approximation (Case 1)
    _, ku1, Tu1 = routh_hurwitz_case1()
    pid = ziegler_nichols_pid(ku1, Tu1, "PID")
    cl_pade = case1_closed_loop_pid(pid.Kp, pid.Ki, pid.Kd)

    # IMC-PI (tau_c = 1.5)
    imc = imc_pi(tau_c=1.5)
    cl_imc = true_plant_pi_closed_loop(imc.Kp, imc.Ki, pade_order=12)

    # SIMC-PI (tight): tau_c = theta = 0.3
    simc_t = simc_pi(tau_c=0.3)
    cl_simc_t = true_plant_pi_closed_loop(simc_t.Kp, simc_t.Ki, pade_order=12)

    # SIMC-PI (smoother): tau_c = 1.5*theta = 0.45
    simc_s = simc_pi(tau_c=0.45)
    cl_simc_s = true_plant_pi_closed_loop(simc_s.Kp, simc_s.Ki, pade_order=12)

    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for sys, label, style in [
        (cl_simc_t, "SIMC-PI ($\\tau_c = \\theta$)", {"ls": "--", "color": "tab:red"}),
        (cl_simc_s, "SIMC-PI ($\\tau_c = 1.5\\theta$)", {"ls": "-.", "color": "tab:cyan"}),
        (cl_imc,    "IMC-PI",                          {"ls": ":",  "color": "k"}),
        (cl_pade,   "Z-N with Pade approx.",           {"ls": "-",  "color": "tab:purple"}),
    ]:
        _, y = ct.step_response(sys, T=t)
        ax.plot(t, y, label=label, **style)

    ax.axhline(1.0, color="k", lw=0.4, alpha=0.4)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Output Response")
    ax.set_title("Comparative closed-loop step response (FOPTD)")
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = fig_path("fig07_controller_comparison.png")
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
