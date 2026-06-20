This repo contains a Python reproduction of our paper on the control of time-delayed first-order processes approximated by the Padé function. The preprint is available on [arXiV](https://arxiv.org/abs/2210.08187).

## Quick Demo

```bash
pip install -e .
python demo.py
```

`demo.py` computes all four controllers (Z-N + Padé, IMC-PI, SIMC-PI tight, SIMC-PI smooth), prints their gains and step-info metrics in one table, and pops up the comparative step-response plot.

## Reproduce Results

Requires Python 3.10+. From the repo root:

```bash
# 1. Install the package and its scientific dependencies (control, scipy, numpy, matplotlib).
pip install -e .

# 2. Regenerate every figure in the paper.
python scripts/fig02_case1_ku_oscillation.py   # Fig. 2  --- Case 1, marginal oscillation at K = ku
python scripts/fig03_nyquist.py                # Fig. 3  --- Nyquist plot of the FOPTD process
python scripts/fig04_case2_ku_oscillation.py   # Fig. 4  --- Case 2, marginal oscillation at K = ku
python scripts/fig05_case1_gain_sweep.py       # Fig. 5  --- 2x2 gain sweep K = 4.6, 5, 7.67, 7.8
python scripts/fig06_case1_vs_case2.py         # Fig. 6  --- Case 1 vs Case 2 closed-loop step response
python scripts/fig07_controller_comparison.py  # Fig. 7  --- Z-N+Padé vs IMC-PI vs SIMC-PI (tight/smooth)

# 3. Regenerate the performance tables.
python scripts/table06_perf_two_cases.py       # Table 6 --- performance for Case 1 vs Case 2
python scripts/table07_perf_all_controllers.py # Table 7 --- performance across all four controllers

# 4. Verify our numerics against the paper's reported values.
pip install -e .[test]
pytest tests/ -v
```

Figures are written to `figures/` and CSV tables to `tables/` (both directories are git-ignored --- regenerate by running the scripts above). The pytest suite asserts (within tolerance) the paper's `ku`, `Tu`, the four PID gain triples, the Nyquist-margin diagnostics for Case 2, and the Table 7 step-info metrics.

### What's in the Package

| Module / dir | Contents |
|---|---|
| `foptd_pade/plant.py`   | FOPTD plant, 1/1 Padé approximant, closed-loop transfer functions |
| `foptd_pade/tuning.py`  | Routh-Hurwitz (Case 1), Nyquist-margin (Case 2), Ziegler-Nichols, IMC, SIMC |
| `foptd_pade/metrics.py` | Step-info (settling, rise, overshoot, peak, ess) computed directly from y(t) |
| `scripts/`              | One CLI script per paper figure (`fig0X_*.py`) and per table (`tableXX_*.py`) |
| `tests/`                | Pytest assertions against paper-reported numerics |

### Caveat

Case 2 (delay-retained) is simulated with a 10–12-order Padé approximant as a numerical proxy for MATLAB's DDE solver. The Z-N + Padé, IMC, and SIMC reproductions match Table 7 to within ~1 %. Case 2 step-info metrics differ from the paper because the Padé proxy smooths the high-frequency DDE artifacts that show up in MATLAB's `dde23` solver.

## Citation

If you find this work useful, please cite us via the following BiBTeX entry:

```bibtex
@online{enweremOptimalControllerTuning2023,
  title = {Optimal {{Controller Tuning Technique}} for a {{First-Order Process}} with {{Time Delay}}},
  author = {Enwerem, Clinton and Okoro, Ihechiluru},
  date = {2023-04-08},
  eprint = {2210.08187},
  eprinttype = {arXiv},
  eprintclass = {eess},
  doi = {10.48550/arXiv.2210.08187},
  url = {http://arxiv.org/abs/2210.08187},
  urldate = {2025-01-09},
  abstract = {We present a controller tuning strategy for first-order plus time delay (FOPTD) processes, where the time delay in the model is approximated using the Pad\textbackslash 'e function. Using Routh-Hurwitz stability analysis, we derive the gain that gives rise to desirable PID controller settings. The resulting PID controller, now correctly tuned, produces satisfactory closed-loop behavior and stabilizes the first-order plant. Our proposed technique eliminates the dead-time component in the model and results in a minimum-phase system with all of its poles and zeros in the left-half \$s\$-plane. To demonstrate the effectiveness of our approach, we present control simulation results from an in-depth performance comparison between our technique and other established model-based strategies used for the control of time-delayed systems. These results prove that, for the FOPTD model, Pad\textbackslash 'e approximation eliminates the undesirable effects of the time delay and promises a faster tracking performance superior to conventional model-based controllers.},
  pubstate = {prepublished},
  keywords = {Computer Science - Systems and Control,Electrical Engineering and Systems Science - Systems and Control,Mathematics - Optimization and Control}
}
```
