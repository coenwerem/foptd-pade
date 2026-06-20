"""Single-script demo of the foptd_pade reproduction.

Computes the four controllers in the paper (Z-N + Pade, IMC-PI, SIMC-PI tight,
SIMC-PI smooth), prints their gains and step-response metrics in one table,
and shows the comparative step-response plot on screen.

Run:
    python demo.py
"""

from __future__ import annotations

import warnings

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from foptd_pade.metrics import step_metrics
from foptd_pade.plant import (
    THETA,
    TAU,
    case1_closed_loop_pid,
    true_plant_pi_closed_loop,
)
from foptd_pade.tuning import (
    imc_pi,
    nyquist_case2_ku_tu,
    routh_hurwitz_case1,
    simc_pi,
    ziegler_nichols_pid,
)


def _row(name, kp, ki, kd, m):
    kd_s = f"{kd:7.3f}" if kd is not None else "      -"
    return (f"{name:<28} {kp:7.3f} {ki:7.3f} {kd_s} "
            f"{m.settling_time:7.3f} {m.rise_time:7.3f} "
            f"{m.peak_amplitude:7.3f} {m.overshoot_pct:7.2f}")


def main() -> None:
    warnings.filterwarnings("ignore")

    print(f"\nFOPTD plant:  G(s) = e^(-{THETA}s) / ({TAU}s + 1)\n")

    # Diagnostic quantities the paper derives
    _, ku1, Tu1 = routh_hurwitz_case1()
    Gm_dB, wc, ku2, Tu2 = nyquist_case2_ku_tu(pade_order=30)
    print("Case 1 (Pade approx., Routh-Hurwitz)")
    print(f"  stability interval:  K in (-1, {ku1:.4f})")
    print(f"  ultimate period:     Tu = {Tu1:.4f} s")
    print()
    print("Case 2 (delay retained, Nyquist gain-margin)")
    print(f"  Gm = {Gm_dB:.4f} dB,  omega_c = {wc:.4f} rad/s")
    print(f"  ku = {ku2:.4f},  Tu = {Tu2:.4f} s")

    # Controllers
    zn  = ziegler_nichols_pid(ku1, Tu1, "PID")
    imc = imc_pi(tau_c=1.5)
    sit = simc_pi(tau_c=0.3)
    sis = simc_pi(tau_c=0.45)

    # Closed loops
    cl_zn   = case1_closed_loop_pid(zn.Kp, zn.Ki, zn.Kd)
    cl_imc  = true_plant_pi_closed_loop(imc.Kp, imc.Ki, pade_order=12)
    cl_sit  = true_plant_pi_closed_loop(sit.Kp, sit.Ki, pade_order=12)
    cl_sis  = true_plant_pi_closed_loop(sis.Kp, sis.Ki, pade_order=12)

    metrics = {name: step_metrics(cl, t_final=20.0) for name, cl in {
        "Z-N + Pade":               cl_zn,
        "IMC-PI":                   cl_imc,
        "SIMC-PI (tau_c = theta)":  cl_sit,
        "SIMC-PI (tau_c = 1.5theta)": cl_sis,
    }.items()}

    print()
    print(f"{'Controller':<28} {'Kp':>7} {'Ki':>7} {'Kd':>7} {'ts':>7} {'tr':>7} {'peak':>7} {'%OS':>7}")
    print("-" * 80)
    print(_row("Z-N + Pade",               zn.Kp, zn.Ki, zn.Kd,  metrics["Z-N + Pade"]))
    print(_row("IMC-PI",                   imc.Kp, imc.Ki, None, metrics["IMC-PI"]))
    print(_row("SIMC-PI (tau_c=theta)",    sit.Kp, sit.Ki, None, metrics["SIMC-PI (tau_c = theta)"]))
    print(_row("SIMC-PI (tau_c=1.5theta)", sis.Kp, sis.Ki, None, metrics["SIMC-PI (tau_c = 1.5theta)"]))

    # Comparative step plot
    t = np.linspace(0.0, 10.0, 8001)
    fig, ax = plt.subplots(figsize=(8.0, 4.8))
    for cl, label, style in [
        (cl_sit, "SIMC-PI ($\\tau_c = \\theta$)",     {"ls": "--", "color": "tab:red"}),
        (cl_sis, "SIMC-PI ($\\tau_c = 1.5\\theta$)",  {"ls": "-.", "color": "tab:cyan"}),
        (cl_imc, "IMC-PI",                            {"ls": ":",  "color": "k"}),
        (cl_zn,  "Z-N with Padé approx.",        {"ls": "-",  "color": "tab:purple"}),
    ]:
        _, y = ct.step_response(cl, T=t)
        ax.plot(t, y, label=label, **style)
    ax.axhline(1.0, color="k", lw=0.4, alpha=0.4)
    ax.grid(alpha=0.3)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Output Response")
    ax.set_title("FOPTD closed-loop step response --- controller comparison (demo)")
    ax.legend(loc="lower right")
    fig.tight_layout()

    print("\nclose the plot window to exit.")
    plt.show()


if __name__ == "__main__":
    main()
