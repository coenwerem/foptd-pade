"""FOPTD plant model and Pade approximants (paper Section 2)."""

from __future__ import annotations

import control as ct
import numpy as np

THETA: float = 0.3
TAU: float = 1.0
K_GAIN: float = 1.0


def pade_plant_tf(theta: float = THETA, tau: float = TAU) -> ct.TransferFunction:
    """1/1 Pade-approximated FOPTD plant (paper Eq. 6).

    G(s) = (-theta*s + 2) / (tau*theta*s^2 + (2*tau + theta)*s + 2)
    """
    num = [-theta, 2.0]
    den = [tau * theta, 2.0 * tau + theta, 2.0]
    return ct.tf(num, den)


def true_plant_high_order_pade(
    theta: float = THETA, tau: float = TAU, order: int = 12
) -> ct.TransferFunction:
    """FOPTD with delay represented by a high-order Pade for numeric simulation."""
    num_delay, den_delay = ct.pade(theta, n=order)
    delay = ct.tf(num_delay, den_delay)
    first_order = ct.tf([1.0], [tau, 1.0])
    return delay * first_order


def case1_closed_loop_p_only(K: float, theta: float = THETA, tau: float = TAU) -> ct.TransferFunction:
    """Closed-loop CL = K*G/(1 + K*G) with G the 1/1-Pade-approximated FOPTD (paper Eq. 7)."""
    num = [-theta * K, 2.0 * K]
    den = [tau * theta, 2.0 * tau + theta - theta * K, 2.0 + 2.0 * K]
    return ct.tf(num, den)


def case1_closed_loop_pid(
    Kp: float, Ki: float, Kd: float, theta: float = THETA, tau: float = TAU
) -> ct.TransferFunction:
    """Closed-loop of 1/1-Pade plant with parallel PID Gc = Kp + Ki/s + Kd*s."""
    G = pade_plant_tf(theta, tau)
    s = ct.tf("s")
    Gc = Kp + Ki / s + Kd * s
    return ct.feedback(Gc * G, 1)


def true_plant_pi_closed_loop(
    Kp: float, Ki: float, theta: float = THETA, tau: float = TAU, pade_order: int = 12
) -> ct.TransferFunction:
    """Closed-loop of the *true-delay* FOPTD plant with a parallel PI controller."""
    G = true_plant_high_order_pade(theta, tau, order=pade_order)
    s = ct.tf("s")
    Gc = Kp + Ki / s
    return ct.feedback(Gc * G, 1)


def true_plant_pid_closed_loop(
    Kp: float, Ki: float, Kd: float, theta: float = THETA, tau: float = TAU, pade_order: int = 12
) -> ct.TransferFunction:
    """Closed-loop of the *true-delay* FOPTD plant with a parallel PID controller."""
    G = true_plant_high_order_pade(theta, tau, order=pade_order)
    s = ct.tf("s")
    Gc = Kp + Ki / s + Kd * s
    return ct.feedback(Gc * G, 1)
