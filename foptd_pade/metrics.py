"""Step-response metrics computed directly from y(t) (mirrors MATLAB stepinfo)."""

from __future__ import annotations

from dataclasses import dataclass

import control as ct
import numpy as np


@dataclass
class StepMetrics:
    settling_time: float  # seconds (2% band, MATLAB default)
    rise_time: float      # seconds (10% -> 90% of final value, MATLAB default)
    overshoot_pct: float
    peak_amplitude: float
    steady_state_error: float


def _final_value(y: np.ndarray, tail_frac: float = 0.05) -> float:
    """Estimate y_final by averaging the last `tail_frac` of the time series."""
    n_tail = max(1, int(tail_frac * len(y)))
    return float(np.mean(y[-n_tail:]))


def _rise_time(t: np.ndarray, y: np.ndarray, y_final: float) -> float:
    """10% -> 90% rise time (MATLAB default for stable, non-decreasing-from-zero responses)."""
    if y_final == 0:
        return float("nan")
    lo = 0.10 * y_final
    hi = 0.90 * y_final
    # find first crossings
    if y_final > 0:
        above_lo = np.where(y >= lo)[0]
        above_hi = np.where(y >= hi)[0]
    else:
        above_lo = np.where(y <= lo)[0]
        above_hi = np.where(y <= hi)[0]
    if above_lo.size == 0 or above_hi.size == 0:
        return float("nan")
    return float(t[above_hi[0]] - t[above_lo[0]])


def _settling_time(t: np.ndarray, y: np.ndarray, y_final: float, band: float = 0.02) -> float:
    """Time after which |y - y_final| stays within band*|y_final| forever (within recorded window)."""
    if y_final == 0:
        return float("nan")
    tol = band * abs(y_final)
    outside = np.where(np.abs(y - y_final) > tol)[0]
    if outside.size == 0:
        return float(t[0])
    last_out = int(outside[-1])
    if last_out + 1 >= len(t):
        return float("inf")
    return float(t[last_out + 1])


def step_metrics(
    sys: ct.TransferFunction,
    t_final: float = 20.0,
    n_points: int = 8000,
    reference: float = 1.0,
) -> StepMetrics:
    """Compute step-response metrics from the closed-loop transfer function."""
    t = np.linspace(0.0, t_final, n_points)
    t_out, y = ct.step_response(sys, T=t)

    y_final = _final_value(y)
    peak = float(np.max(y))
    overshoot = 100.0 * max(0.0, (peak - y_final) / y_final) if y_final != 0 else 0.0

    return StepMetrics(
        settling_time=_settling_time(t_out, y, y_final),
        rise_time=_rise_time(t_out, y, y_final),
        overshoot_pct=overshoot,
        peak_amplitude=peak,
        steady_state_error=float(reference - y_final),
    )
