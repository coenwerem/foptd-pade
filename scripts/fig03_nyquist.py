"""Figure 3: Nyquist plot of the FOPTD process (with the true delay)."""

from __future__ import annotations

import control as ct
import matplotlib.pyplot as plt
import numpy as np

from _common import configure_mpl, fig_path  # noqa: E402

from foptd_pade.plant import true_plant_high_order_pade


def main() -> None:
    configure_mpl()
    G = true_plant_high_order_pade(order=30)

    omega = np.logspace(-2, 2, 4000)
    # Manual response computation to control the look
    s = 1j * omega
    resp = ct.frequency_response(G, omega)
    H = resp.fresp[0, 0, :]

    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.plot(H.real, H.imag, color="tab:blue", label="$j\\omega > 0$")
    ax.plot(H.real, -H.imag, color="tab:blue", ls="--", alpha=0.7, label="$j\\omega < 0$")
    ax.plot(-1.0, 0.0, "r+", ms=12, mew=2, label="$-1 + j0$")

    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.9, 0.9)
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.set_title("Nyquist Diagram of the FOPTD Process")
    ax.legend(loc="upper right")
    ax.set_aspect("equal")
    fig.tight_layout()
    out = fig_path("fig03_nyquist.png")
    fig.savefig(out)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
