"""Figure 3: Nyquist plot of the FOPTD process (with the true delay)."""

from __future__ import annotations

import control as ct
import numpy as np

from _common import configure_mpl, new_figure, save_figure  # noqa: E402

from foptd_pade.plant import true_plant_high_order_pade


def main() -> None:
    configure_mpl()
    G = true_plant_high_order_pade(order=30)

    omega = np.logspace(-2, 2, 4000)
    resp = ct.frequency_response(G, omega)
    H = resp.frdata[0, 0, :]

    fig, ax = new_figure(figsize=(5.5, 5.5),
                         left=0.18, right=0.97, bottom=0.13, top=0.97)
    ax.plot(H.real, H.imag, color="tab:blue", label="$j\\omega > 0$")
    ax.plot(H.real, -H.imag, color="tab:blue", ls="--", alpha=0.7, label="$j\\omega < 0$")
    ax.plot(-1.0, 0.0, "r+", ms=12, mew=2, label="$-1 + j0$")
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)
    ax.grid(True)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-0.9, 0.9)
    ax.set_xlabel("Real Axis")
    ax.set_ylabel("Imaginary Axis")
    ax.legend(loc="upper right")
    ax.set_aspect("equal")
    png, pdf = save_figure(fig, "fig03_nyquist")
    print(f"wrote {png}\nwrote {pdf}")


if __name__ == "__main__":
    main()
