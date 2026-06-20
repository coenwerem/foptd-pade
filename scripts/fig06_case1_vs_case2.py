"""Figure 6: Case 1 (Pade-tuned PID on Pade plant) vs Case 2 (delay-retained PID on true plant)."""

from __future__ import annotations

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from _common import configure_mpl, fig_path  # noqa: E402

from foptd_pade.plant import case1_closed_loop_pid, true_plant_pid_closed_loop
from foptd_pade.tuning import (
    nyquist_case2_ku_tu,
    routh_hurwitz_case1,
    ziegler_nichols_pid,
)


def main() -> None:
    configure_mpl()

    _, ku1, Tu1 = routh_hurwitz_case1()
    pid1 = ziegler_nichols_pid(ku1, Tu1, "PID")
    cl_case1 = case1_closed_loop_pid(pid1.Kp, pid1.Ki, pid1.Kd)

    _, _, ku2, Tu2 = nyquist_case2_ku_tu(pade_order=30)
    pid2 = ziegler_nichols_pid(ku2, Tu2, "PID")
    cl_case2 = true_plant_pid_closed_loop(pid2.Kp, pid2.Ki, pid2.Kd, pade_order=10)

    t = np.linspace(0.0, 10.0, 8001)
    _, y1 = ct.step_response(cl_case1, T=t)
    _, y2 = ct.step_response(cl_case2, T=t)

    fig, ax = plt.subplots()
    ax.plot(t, y1, color="tab:red", label="Case 1 (Pade approx.)")
    ax.plot(t, y2, color="k", ls="-.", label="Case 2 (delay retained)")
    ax.axhline(1.0, color="k", lw=0.5, alpha=0.5)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Output Response")
    ax.set_title("Case 1 vs Case 2 closed-loop step response")
    ax.legend()
    fig.tight_layout()
    out = fig_path("fig06_case1_vs_case2.png")
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
