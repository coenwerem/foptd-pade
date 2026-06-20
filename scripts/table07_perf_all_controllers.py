"""Table 7: gains & performance for all four controllers."""

from __future__ import annotations

import csv

from _common import table_path  # noqa: E402

from foptd_pade.metrics import step_metrics
from foptd_pade.plant import case1_closed_loop_pid, true_plant_pi_closed_loop
from foptd_pade.tuning import (
    imc_pi,
    routh_hurwitz_case1,
    simc_pi,
    ziegler_nichols_pid,
)

PAPER = {
    "Z-N + Pade":              {"Kp": 4.600, "Ki": 11.194, "Kd": 0.473,
                                "ts": 1.83, "tr": 0.14, "OS": 44.08, "peak": 1.44, "ess": 0.00},
    "IMC-PI":                  {"Kp": 0.555, "Ki": 0.555,  "Kd": None,
                                "ts": 5.99, "tr": 3.22, "OS": 0.00,  "peak": 0.999, "ess": 0.00},
    "SIMC-PI (tau_c=theta)":   {"Kp": 1.67,  "Ki": 1.67,   "Kd": None,
                                "ts": 1.82, "tr": 0.57, "OS": 4.12,  "peak": 1.04,  "ess": 0.00},
    "SIMC-PI (tau_c=1.5theta)":{"Kp": 1.33,  "Ki": 1.33,   "Kd": None,
                                "ts": 1.64, "tr": 0.85, "OS": 0.07,  "peak": 1.00,  "ess": 0.00},
}


def main() -> None:
    _, ku, Tu = routh_hurwitz_case1()
    zn   = ziegler_nichols_pid(ku, Tu, "PID")
    imc  = imc_pi(tau_c=1.5)
    sit  = simc_pi(tau_c=0.3)
    sis  = simc_pi(tau_c=0.45)

    sysmap = {
        "Z-N + Pade":               (zn,  case1_closed_loop_pid(zn.Kp, zn.Ki, zn.Kd)),
        "IMC-PI":                   (imc, true_plant_pi_closed_loop(imc.Kp, imc.Ki, pade_order=12)),
        "SIMC-PI (tau_c=theta)":    (sit, true_plant_pi_closed_loop(sit.Kp, sit.Ki, pade_order=12)),
        "SIMC-PI (tau_c=1.5theta)": (sis, true_plant_pi_closed_loop(sis.Kp, sis.Ki, pade_order=12)),
    }

    header = f"{'Controller':<28} {'Kp':>7} {'Ki':>7} {'Kd':>7} {'ts':>7} {'tr':>7} {'peak':>7} {'%OS':>7} {'ess':>7}"
    print(header)
    print("-" * len(header))

    out_csv = table_path("table07.csv")
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["controller", "source",
                    "Kp", "Ki", "Kd", "ts_s", "tr_s", "peak_amp", "OS_pct", "ess"])

        for name, (gains, cl) in sysmap.items():
            m = step_metrics(cl, t_final=20.0)
            print(f"{name:<28} {gains.Kp:7.3f} {gains.Ki:7.3f} {gains.Kd:7.3f} "
                  f"{m.settling_time:7.3f} {m.rise_time:7.3f} {m.peak_amplitude:7.3f} "
                  f"{m.overshoot_pct:7.2f} {m.steady_state_error:7.3f}")
            paper = PAPER[name]
            kd_p = paper["Kd"] if paper["Kd"] is not None else 0.0
            print(f"{'  (paper)':<28} {paper['Kp']:7.3f} {paper['Ki']:7.3f} {kd_p:7.3f} "
                  f"{paper['ts']:7.3f} {paper['tr']:7.3f} {paper['peak']:7.3f} "
                  f"{paper['OS']:7.2f} {paper['ess']:7.3f}")
            w.writerow([name, "ours",
                        f"{gains.Kp:.4f}", f"{gains.Ki:.4f}", f"{gains.Kd:.4f}",
                        f"{m.settling_time:.4f}", f"{m.rise_time:.4f}",
                        f"{m.peak_amplitude:.4f}", f"{m.overshoot_pct:.4f}",
                        f"{m.steady_state_error:.4f}"])
            w.writerow([name, "paper",
                        f"{paper['Kp']}", f"{paper['Ki']}", f"{kd_p}",
                        f"{paper['ts']}", f"{paper['tr']}",
                        f"{paper['peak']}", f"{paper['OS']}", f"{paper['ess']}"])

    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
