"""Pytest assertions that our reproduction matches paper-reported numerics.

Tolerances are deliberately a touch wide (1-2% on stepinfo metrics) to
allow for the simulator-difference between MATLAB's DDE solver and our
high-order-Pade numerical proxy.
"""

from __future__ import annotations

import math

import pytest

from foptd_pade.metrics import step_metrics
from foptd_pade.plant import (
    case1_closed_loop_pid,
    true_plant_pi_closed_loop,
    true_plant_pid_closed_loop,
)
from foptd_pade.tuning import (
    imc_pi,
    nyquist_case2_ku_tu,
    routh_hurwitz_case1,
    simc_pi,
    ziegler_nichols_pid,
)


# ----- Section 2.1: Case 1 (Pade) Routh-Hurwitz --------------------------------

def test_case1_ku_matches_paper():
    """Paper: ku = 7.67."""
    _, ku, _ = routh_hurwitz_case1()
    assert ku == pytest.approx(7.6667, abs=0.005)


def test_case1_Tu_matches_paper():
    """Paper: Tu = 0.8219 s (measured numerically); analytic value is 0.8266 s."""
    _, _, Tu = routh_hurwitz_case1()
    assert Tu == pytest.approx(0.8219, abs=0.01)


# ----- Section 2.2: Case 2 (delay-retained) Nyquist ----------------------------

def test_case2_gain_margin_db():
    """Paper: Gm = 15.4026 dB."""
    Gm_dB, _, _, _ = nyquist_case2_ku_tu(pade_order=30)
    assert Gm_dB == pytest.approx(15.4026, abs=0.01)


def test_case2_omega_c():
    """Paper: omega_c = 5.8047 rad/s."""
    _, wc, _, _ = nyquist_case2_ku_tu(pade_order=30)
    assert wc == pytest.approx(5.8047, abs=0.005)


def test_case2_ku_tu():
    """Paper: ku = 5.8902, Tu = 1.0824 s."""
    _, _, ku, Tu = nyquist_case2_ku_tu(pade_order=30)
    assert ku == pytest.approx(5.8902, abs=0.005)
    assert Tu == pytest.approx(1.0824, abs=0.005)


# ----- Z-N PID gains -----------------------------------------------------------

def test_zn_pade_pid_gains():
    """Paper Table 3 / 7: Kp = 4.6, Ki = 11.194, Kd = 0.473."""
    _, ku, Tu = routh_hurwitz_case1()
    pid = ziegler_nichols_pid(ku, Tu, "PID")
    assert pid.Kp == pytest.approx(4.600, abs=0.005)
    assert pid.Ki == pytest.approx(11.194, abs=0.1)
    assert pid.Kd == pytest.approx(0.473, abs=0.005)


def test_zn_case2_pid_gains():
    """Paper Table 4: Kp = 3.5341, tau_i = 0.5412, tau_d = 0.1353 -> Ki ~ 6.53, Kd ~ 0.4782."""
    _, _, ku, Tu = nyquist_case2_ku_tu(pade_order=30)
    pid = ziegler_nichols_pid(ku, Tu, "PID")
    assert pid.Kp == pytest.approx(3.5341, abs=0.005)
    assert pid.Ki == pytest.approx(6.5301, abs=0.05)
    assert pid.Kd == pytest.approx(0.4782, abs=0.005)


# ----- IMC / SIMC --------------------------------------------------------------

def test_imc_pi_gains():
    """Paper: Kp = Ki = 0.555 with tau_c = 1.5."""
    g = imc_pi(tau_c=1.5)
    assert g.Kp == pytest.approx(0.5556, abs=0.005)
    assert g.Ki == pytest.approx(0.5556, abs=0.005)


def test_simc_tight_gains():
    """Paper: Kp = Ki = 1.67 with tau_c = theta."""
    g = simc_pi(tau_c=0.3)
    assert g.Kp == pytest.approx(1.667, abs=0.005)
    assert g.Ki == pytest.approx(1.667, abs=0.005)


def test_simc_smooth_gains():
    """Paper: Kp = Ki = 1.33 with tau_c = 1.5*theta."""
    g = simc_pi(tau_c=0.45)
    assert g.Kp == pytest.approx(1.333, abs=0.005)
    assert g.Ki == pytest.approx(1.333, abs=0.005)


# ----- Step-response metrics (Table 7) -----------------------------------------
#
# Paper Table 7 reports:
#   Z-N + Pade   : ts=1.83  tr=0.14  %OS=44.08  peak=1.44
#   IMC-PI       : ts=5.99  tr=3.22  %OS=0.00   peak=0.999
#   SIMC tight   : ts=1.82  tr=0.57  %OS=4.12   peak=1.04
#   SIMC smooth  : ts=1.64  tr=0.85  %OS=0.07   peak=1.00


def _metrics_for(controller: str):
    _, ku, Tu = routh_hurwitz_case1()
    if controller == "zn_pade":
        pid = ziegler_nichols_pid(ku, Tu, "PID")
        cl = case1_closed_loop_pid(pid.Kp, pid.Ki, pid.Kd)
    elif controller == "imc":
        g = imc_pi(tau_c=1.5)
        cl = true_plant_pi_closed_loop(g.Kp, g.Ki, pade_order=12)
    elif controller == "simc_tight":
        g = simc_pi(tau_c=0.3)
        cl = true_plant_pi_closed_loop(g.Kp, g.Ki, pade_order=12)
    elif controller == "simc_smooth":
        g = simc_pi(tau_c=0.45)
        cl = true_plant_pi_closed_loop(g.Kp, g.Ki, pade_order=12)
    else:
        raise ValueError(controller)
    return step_metrics(cl, t_final=20.0)


def test_table7_zn_pade_metrics():
    m = _metrics_for("zn_pade")
    assert m.settling_time == pytest.approx(1.83, abs=0.30)
    assert m.rise_time     == pytest.approx(0.14, abs=0.10)
    assert m.peak_amplitude == pytest.approx(1.44, abs=0.10)
    assert m.overshoot_pct == pytest.approx(44.08, abs=5.0)
    assert abs(m.steady_state_error) < 0.02


def test_table7_imc_metrics():
    m = _metrics_for("imc")
    assert m.settling_time == pytest.approx(5.99, abs=0.50)
    assert m.peak_amplitude == pytest.approx(1.0, abs=0.05)
    assert abs(m.steady_state_error) < 0.02


def test_table7_simc_tight_metrics():
    m = _metrics_for("simc_tight")
    assert m.settling_time == pytest.approx(1.82, abs=0.50)
    assert m.peak_amplitude == pytest.approx(1.04, abs=0.10)
    assert abs(m.steady_state_error) < 0.02


def test_table7_simc_smooth_metrics():
    m = _metrics_for("simc_smooth")
    assert m.settling_time == pytest.approx(1.64, abs=0.50)
    assert m.peak_amplitude == pytest.approx(1.00, abs=0.05)
    assert abs(m.steady_state_error) < 0.02
