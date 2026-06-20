"""Controller-tuning rules used in the paper.

All formulas come directly from the paper:
- Routh-Hurwitz (Case 1): paper Section 2.1.i
- Nyquist (Case 2):       paper Eqs. (9)-(11)
- Ziegler-Nichols rules:  paper Table 2
- IMC PI:                 paper Eqs. (13a)-(13b)
- SIMC PI:                paper Eqs. (15)-(16)
"""

from __future__ import annotations

from dataclasses import dataclass

import control as ct
import numpy as np

from .plant import THETA, TAU, K_GAIN, true_plant_high_order_pade


@dataclass
class PIDGains:
    Kp: float
    Ki: float
    Kd: float

    @property
    def tau_i(self) -> float | None:
        return self.Kp / self.Ki if self.Ki != 0 else None

    @property
    def tau_d(self) -> float | None:
        return self.Kd / self.Kp if self.Kp != 0 else None


def routh_hurwitz_case1(theta: float = THETA, tau: float = TAU) -> tuple[float, float, float]:
    """Return (K_lower_bound, K_upper_bound = ku, Tu) for Case 1 (Pade-approximated).

    From Routh array on Eq. (7):
        s^1 coefficient: 2*tau + theta - theta*K  > 0   =>   K < (2*tau + theta)/theta = 2*tau/theta + 1
        s^0 coefficient: 2 + 2*K                  > 0   =>   K > -1

    Tu is computed numerically from the marginal step response.
    """
    K_lb = -1.0
    ku = 2.0 * tau / theta + 1.0  # = 7.6667 for theta=0.3, tau=1
    # At K = ku, the closed loop has poles at s = +- j*sqrt((2+2*ku)/(tau*theta))
    # Tu = 2*pi / omega_u, where omega_u = sqrt((2+2*ku)/(tau*theta))
    omega_u = np.sqrt((2.0 + 2.0 * ku) / (tau * theta))
    Tu = 2.0 * np.pi / omega_u
    return K_lb, ku, Tu


def nyquist_case2_ku_tu(theta: float = THETA, tau: float = TAU, pade_order: int = 30) -> tuple[float, float, float, float]:
    """Case 2: read off (Gm_dB, omega_c, ku, Tu) from the gain margin of the true-delay plant.

    ku = 10^(Gm_dB/20), Tu = 2*pi / omega_c.
    """
    G = true_plant_high_order_pade(theta, tau, order=pade_order)
    gm, _pm, wcg, _wcp = ct.margin(G)
    Gm_dB = 20.0 * np.log10(gm)
    ku = 10.0 ** (Gm_dB / 20.0)  # equals gm by construction; kept for clarity
    Tu = 2.0 * np.pi / wcg
    return Gm_dB, wcg, ku, Tu


def ziegler_nichols_pid(ku: float, Tu: float, kind: str = "PID") -> PIDGains:
    """Z-N classical tuning rules from paper Table 2.

    Returns PIDGains with parallel-form (Kp, Ki, Kd) where Ki = Kp/tau_i, Kd = Kp*tau_d.
    """
    if kind == "P":
        Kp = 0.5 * ku
        return PIDGains(Kp=Kp, Ki=0.0, Kd=0.0)
    if kind == "PI":
        Kp = 0.45 * ku
        tau_i = 0.83 * Tu
        return PIDGains(Kp=Kp, Ki=Kp / tau_i, Kd=0.0)
    if kind == "PID":
        Kp = 0.6 * ku
        tau_i = 0.5 * Tu
        tau_d = 0.125 * Tu
        return PIDGains(Kp=Kp, Ki=Kp / tau_i, Kd=Kp * tau_d)
    raise ValueError(f"unknown Z-N controller kind: {kind!r}")


def imc_pi(tau_c: float = 1.5, k: float = K_GAIN, tau: float = TAU, theta: float = THETA) -> PIDGains:
    """IMC PI controller for the FOPTD plant (paper Eq. 13).

    Gc(s) = (tau*s + 1) / (k*(tau_c + theta)*s) ~= Kp + Ki/s
    with Kp = tau / (k*(tau_c + theta)),  Ki = 1 / (k*(tau_c + theta)).
    """
    denom = k * (tau_c + theta)
    Kp = tau / denom
    Ki = 1.0 / denom
    return PIDGains(Kp=Kp, Ki=Ki, Kd=0.0)


def simc_pi(tau_c: float, k: float = K_GAIN, tau1: float = TAU, theta: float = THETA) -> PIDGains:
    """SIMC PI controller (Grimholt & Skogestad / paper Eqs. 15-16).

        Kc = (1/k) * tau1 / (tau_c + theta)
        tau_i = min(tau1, 4*(tau_c + theta))
        Ki = Kc / tau_i
    """
    Kc = (1.0 / k) * tau1 / (tau_c + theta)
    tau_i = min(tau1, 4.0 * (tau_c + theta))
    Ki = Kc / tau_i
    return PIDGains(Kp=Kc, Ki=Ki, Kd=0.0)
