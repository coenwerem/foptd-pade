"""Table 6: performance metrics for Case 1 (Pade) and Case 2 (delay retained)."""

from __future__ import annotations

import csv

from _common import table_path  # noqa: E402

from foptd_pade.metrics import step_metrics
from foptd_pade.plant import case1_closed_loop_pid, true_plant_pid_closed_loop
from foptd_pade.tuning import (
    nyquist_case2_ku_tu,
    routh_hurwitz_case1,
    ziegler_nichols_pid,
)


def main() -> None:
    _, ku1, Tu1 = routh_hurwitz_case1()
    pid1 = ziegler_nichols_pid(ku1, Tu1, "PID")
    cl1 = case1_closed_loop_pid(pid1.Kp, pid1.Ki, pid1.Kd)
    m1 = step_metrics(cl1, t_final=20.0)

    _, _, ku2, Tu2 = nyquist_case2_ku_tu(pade_order=30)
    pid2 = ziegler_nichols_pid(ku2, Tu2, "PID")
    cl2 = true_plant_pid_closed_loop(pid2.Kp, pid2.Ki, pid2.Kd, pade_order=10)
    m2 = step_metrics(cl2, t_final=20.0)

    rows = [
        ("Case 1 (Pade)",    m1, 1.83, 0.13, 1.44, 44.1, 0.0),
        ("Case 2 (delay)",   m2, 1.70, 0.12, 1.56, 56.4, 0.0),
    ]

    print(f"{'Case':<18} {'ts':>8} {'tr':>8} {'peak':>8} {'%OS':>8} {'ess':>8}   (paper in parens)")
    out_csv = table_path("table06.csv")
    with out_csv.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["case", "ts_ours", "ts_paper", "tr_ours", "tr_paper",
                    "peak_ours", "peak_paper", "OS_ours_pct", "OS_paper_pct",
                    "ess_ours", "ess_paper"])
        for name, m, ts_p, tr_p, peak_p, os_p, ess_p in rows:
            print(f"{name:<18} {m.settling_time:8.3f} {m.rise_time:8.3f} "
                  f"{m.peak_amplitude:8.3f} {m.overshoot_pct:8.2f} {m.steady_state_error:8.3f}")
            print(f"{'  (paper)':<18} {ts_p:8.3f} {tr_p:8.3f} {peak_p:8.3f} {os_p:8.2f} {ess_p:8.3f}")
            w.writerow([name,
                        f"{m.settling_time:.3f}", f"{ts_p}",
                        f"{m.rise_time:.3f}",     f"{tr_p}",
                        f"{m.peak_amplitude:.3f}", f"{peak_p}",
                        f"{m.overshoot_pct:.2f}", f"{os_p}",
                        f"{m.steady_state_error:.3f}", f"{ess_p}"])
    print(f"wrote {out_csv}")


if __name__ == "__main__":
    main()
