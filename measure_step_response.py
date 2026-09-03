#!/usr/bin/env python3
"""Equilibrium step-response measurement for LSPR sensorgrams.

Each measurement in a record is a shift in light incidence: a narrow downward
transient in the response, after which the signal relaxes to a new equilibrium
level.  The quantity of interest is the *equilibrium* change in response across
that transient.

The estimator has three parts.

1. Detection.  Switch transients are located as prominent, narrow minima of the
   response.  Prominence is topological persistence -- the depth a feature keeps
   before it merges into a larger one -- so it is scale-free and a noise wiggle
   can never acquire the prominence of a real transient.  Width separates the
   narrow switch transient from the wide regeneration excursion.  Detection runs
   on a Gaussian-smoothed copy of the signal; the Gaussian is not cosmetic, it is
   the unique kernel whose scale-space creates no new extrema as sigma grows
   (Babaud et al. 1986; Lindeberg 1990), so smoothing cannot invent a transient.
   Its sigma is specified in seconds and converted with the sampling interval.

2. Segmentation.  The wide regeneration excursions partition the record into
   cycles.  Each cycle yields at most one measurement -- its most prominent
   switch transient -- so the number of reported measurements is fixed by the
   structure of the record, not by a threshold.

3. Estimation.  All estimation uses the *raw* signal, never the smoothed copy.
   The pre-switch level comes from a straight-line fit on the approach, evaluated
   at the switch time.  The post-switch level is the asymptote A of a first-order
   relaxation

       y(t) = A + C exp(-(t - t0) / tau),

   fitted from the end of a guard band to the plateau maximum.  For fixed tau the
   model is linear in (A, C), so tau is profiled on a geometric grid and the
   linear part solved exactly: no initial guess and no convergence failure.  The
   measurement is A minus the pre-switch level.

   Reporting the fitted asymptote rather than the response at some fixed delay
   removes the bias from the plateau drift, which otherwise makes the answer
   depend on how long one happened to wait after the switch.

Both fits carry a covariance, so every measurement is reported with a standard
uncertainty and a 95 % confidence interval (effective degrees of freedom by the
Welch-Satterthwaite formula, as in the GUM).  Events whose fit is unreliable are
rejected with a stated reason rather than reported.

Usage:
    python measure_step_response.py                     # ./data -> ./output
    python measure_step_response.py --data D --out O
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks
from scipy.stats import t as student_t

# Relaxation time constants are searched over this range, in seconds.  A fitted
# tau landing on either end means the model did not describe the segment, and the
# event is rejected.
TAU_MIN_S, TAU_MAX_S = 2.0, 400.0

# A relaxation fit needs a segment appreciably longer than the three parameters.
MIN_POST_SAMPLES = 30

# The shortest approach a straight-line level estimate is allowed to use.  Only
# the first transient of a record ever comes close to it.
MIN_PRE_SAMPLES = 8


def read_record(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Read time and response columns, accepting comma decimal separators."""
    times, responses = [], []
    with open(path, "r", encoding="unicode_escape") as handle:
        next(handle, None)  # column headers
        for line in handle:
            fields = line.split()
            if len(fields) < 2:
                continue
            times.append(float(fields[0].replace(",", ".")))
            responses.append(float(fields[1].replace(",", ".")))
    return np.asarray(times, dtype=float), np.asarray(responses, dtype=float)


def robust_noise_scale(y: np.ndarray) -> float:
    """Noise scale from first differences.

    1.4826 * MAD is a consistent estimator of sigma for Gaussian data with a 50 %
    breakdown point, so the large regeneration excursions cannot inflate it; the
    sqrt(2) undoes the variance doubling introduced by differencing.
    """
    d = np.diff(y)
    return float(1.4826 * np.median(np.abs(d - np.median(d))) / np.sqrt(2.0))


def fit_level(
    t: np.ndarray, y: np.ndarray, t0: float
) -> tuple[float, float, float, int]:
    """OLS straight line, evaluated at t0.  Returns (level, slope, variance, dof)."""
    X = np.column_stack([np.ones_like(t), t - t0])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    dof = max(len(t) - 2, 1)
    s2 = float(resid @ resid) / dof
    cov = s2 * np.linalg.inv(X.T @ X)
    # t is centred on t0, so beta[0] is already the level at t0.
    return float(beta[0]), float(beta[1]), float(cov[0, 0]), dof


def fit_relaxation(
    t: np.ndarray, y: np.ndarray, t0: float
) -> tuple[float, float, float, float, int]:
    """Fit y = A + C exp(-(t - t0) / tau).  Returns (A, C, var(A), tau, dof)."""
    dt_rel = t - t0

    def best_on_grid(grid: np.ndarray) -> tuple[float, float, float, float]:
        best = None
        for tau in grid:
            basis = np.exp(-dt_rel / tau)
            X = np.column_stack([np.ones_like(basis), basis])
            beta, *_ = np.linalg.lstsq(X, y, rcond=None)
            resid = y - X @ beta
            rss = float(resid @ resid)
            if best is None or rss < best[0]:
                best = (rss, float(beta[0]), float(beta[1]), float(tau))
        return best

    coarse = best_on_grid(np.geomspace(TAU_MIN_S, TAU_MAX_S, 60))
    # Refine within one grid step of the coarse optimum.
    span = (TAU_MAX_S / TAU_MIN_S) ** (1.0 / 59)
    rss, A, C, tau = best_on_grid(
        np.geomspace(
            max(coarse[3] / span, TAU_MIN_S), min(coarse[3] * span, TAU_MAX_S), 40
        )
    )

    # Asymptotic covariance from the full Jacobian of (A, C, tau).  Including the
    # tau column matters: conditioning on the profiled tau would understate u(A).
    basis = np.exp(-dt_rel / tau)
    J = np.column_stack([np.ones_like(basis), basis, C * basis * dt_rel / tau**2])
    dof = max(len(t) - 3, 1)
    s2 = rss / dof
    cov = s2 * np.linalg.pinv(J.T @ J)
    return A, C, float(cov[0, 0]), tau, dof


def measure_record(t: np.ndarray, y: np.ndarray, args) -> tuple[list[dict], list[str]]:
    """Locate switch transients and estimate the equilibrium step at each."""
    n = len(t)
    dt = float(np.median(np.diff(t)))
    sigma_noise = robust_noise_scale(y)

    # --- detection, on a smoothed copy only ------------------------------------
    sigma_samples = args.detect_sigma / dt
    y_smooth = gaussian_filter1d(y, sigma_samples) if sigma_samples >= 0.5 else y.copy()
    inverted = -y_smooth  # transients are minima of the response
    # The prominence gate is set by the noise, not by the record's range: switch
    # transients vary in depth over more than an order of magnitude, so a gate
    # tied to the range discards the shallow ones, while noise never accumulates
    # the persistence of a real transient.
    min_prominence = args.min_prominence * sigma_noise
    # Regeneration excursions are told apart from switch transients by depth, not
    # by duration.  A regeneration is several thousand pm deep against at most a
    # few hundred for a switch, an order of magnitude of clear air; their
    # durations, by contrast, overlap as soon as an excursion is clipped by the
    # end of a record, which makes a width test fail silently.
    cycle_prominence = args.cycle_depth * float(np.ptp(y))

    cycles, _ = find_peaks(inverted, prominence=cycle_prominence)
    switches, switch_props = find_peaks(
        inverted,
        prominence=(
            (min_prominence, cycle_prominence)
            if cycle_prominence > min_prominence
            else min_prominence
        ),
        width=(None, args.switch_width / dt),
    )

    edges = [0, *cycles.tolist(), n - 1]
    guard = max(int(round(args.guard / dt)), 1)
    pre_len = max(int(round(args.pre_window / dt)), MIN_PRE_SAMPLES)

    results: list[dict] = []
    notes: list[str] = []

    def estimate(k: int, lo: int, hi: int) -> tuple[dict | None, str]:
        """Measure the step at candidate k, or say why it cannot be measured."""
        i = int(switches[k])
        t0 = float(t[i])

        # The approach is whatever was actually recorded before the transient.
        # The first transient of a record sits only tens of seconds in, so the
        # window is truncated rather than the event discarded; a short baseline
        # is a weaker level estimate and the reported uncertainty says so.
        pre_lo = max(i - guard - pre_len, lo)
        pre_hi = i - guard
        if pre_hi - pre_lo < MIN_PRE_SAMPLES:
            return None, f"approach only {max(pre_hi - pre_lo, 0)} samples before guard band"

        # The relaxation is fitted out to the plateau maximum, which is where the
        # response has settled and before the next regeneration excursion starts.
        post_lo = i + guard
        search_hi = min(hi + 1, post_lo + int(round(args.post_window / dt)))
        if search_hi - post_lo < MIN_POST_SAMPLES:
            return None, f"plateau shorter than {MIN_POST_SAMPLES} samples"
        post_hi = post_lo + int(np.argmax(y_smooth[post_lo:search_hi])) + 1
        if post_hi - post_lo < MIN_POST_SAMPLES:
            return None, "response still falling after guard band"

        pre_level, pre_slope, var_pre, dof_pre = fit_level(
            t[pre_lo:pre_hi], y[pre_lo:pre_hi], t0
        )
        asymptote, amplitude, var_post, tau, dof_post = fit_relaxation(
            t[post_lo:post_hi], y[post_lo:post_hi], t0
        )

        if not TAU_MIN_S * 1.01 < tau < TAU_MAX_S * 0.99:
            return None, f"tau={tau:.1f} s at search boundary"

        step = asymptote - pre_level
        u = float(np.sqrt(var_pre + var_post))
        if u <= 0.0:
            return None, "degenerate fit"
        t_stat = step / u

        if abs(step) < args.min_snr * sigma_noise:
            return None, (f"step {step:+.1f} pm below {args.min_snr:g}x noise "
                          f"({sigma_noise:.2f} pm)")
        # A statistical test cannot separate a small-but-real feature from a
        # small-but-uninteresting one; that needs knowledge of the instrument.
        # This is the one place a prior on the measurement's size enters, and it
        # is off unless asked for.
        if abs(step) < args.min_step:
            return None, f"step {step:+.1f} pm below --min-step {args.min_step:g} pm"
        if abs(t_stat) < args.min_tstat:
            return None, f"|t|={abs(t_stat):.1f} below {args.min_tstat:g}"

        # Welch-Satterthwaite effective degrees of freedom for the combination.
        dof_eff = (var_pre + var_post) ** 2 / (
            var_pre**2 / dof_pre + var_post**2 / dof_post
        )
        ci = float(student_t.ppf(0.975, dof_eff)) * u

        return (
            dict(
                index=i,
                t_switch=t0,
                step=step,
                u=u,
                ci95_lo=step - ci,
                ci95_hi=step + ci,
                tau=tau,
                t_stat=t_stat,
                prominence=float(switch_props["prominences"][k]),
                width=float(switch_props["widths"][k]) * dt,
                pre_level=pre_level,
                pre_slope=pre_slope,
                asymptote=asymptote,
                amplitude=amplitude,
                pre_slice=(pre_lo, pre_hi),
                post_slice=(post_lo, post_hi),
                n_pre=pre_hi - pre_lo,
                n_post=post_hi - post_lo,
            ),
            "",
        )

    for lo, hi in zip(edges[:-1], edges[1:]):
        # One measurement per cycle, but try the candidates deepest first and keep
        # the first that can actually be measured, so a cycle is not lost because
        # its most prominent feature happens to sit against the record's edge.
        inside = sorted(
            (k for k, idx in enumerate(switches) if lo < idx < hi),
            key=lambda k: -switch_props["prominences"][k],
        )
        for k in inside:
            result, reason = estimate(k, lo, hi)
            if result is not None:
                results.append(result)
                break
            notes.append(f"t={t[int(switches[k])]:8.1f} s  rejected: {reason}")

    return results, notes


def plot_record(t, y, results, title, dest_fit: Path, dest_plain: Path) -> None:
    """Two figures: the fitted model over the data, and the bare sensorgram."""
    for dest, annotate in ((dest_fit, True), (dest_plain, False)):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(t, y, lw=0.8, color="0.35", zorder=1)

        if annotate:
            for r in results:
                t0 = r["t_switch"]
                pre_lo, pre_hi = r["pre_slice"]
                post_lo, post_hi = r["post_slice"]

                # pre-switch line, extrapolated to the switch time
                t_pre = np.array([t[pre_lo], t0])
                ax.plot(
                    t_pre,
                    r["pre_level"] + r["pre_slope"] * (t_pre - t0),
                    color="tab:red",
                    lw=1.4,
                    zorder=3,
                )

                # fitted relaxation and its asymptote
                t_post = t[post_lo:post_hi]
                ax.plot(
                    t_post,
                    r["asymptote"] + r["amplitude"] * np.exp(-(t_post - t0) / r["tau"]),
                    color="tab:green",
                    lw=1.6,
                    zorder=3,
                )
                ax.hlines(r["asymptote"], t0, t_post[-1], color="tab:green",
                          ls=":", lw=1.0, zorder=2)

                ax.plot(t0, r["pre_level"], "o", color="tab:red", ms=5, zorder=4)
                ax.plot(t_post[-1], r["asymptote"], "o", color="tab:green", ms=5, zorder=4)

                # the measurement itself
                ax.annotate(
                    "",
                    xy=(t0, r["asymptote"]),
                    xytext=(t0, r["pre_level"]),
                    arrowprops=dict(arrowstyle="<->", color="k", lw=1.0),
                    zorder=4,
                )
                ax.annotate(
                    f"{r['step']:.1f} $\\pm$ {r['u']:.1f} pm",
                    xy=(t0, 0.5 * (r["pre_level"] + r["asymptote"])),
                    xytext=(6, 0),
                    textcoords="offset points",
                    fontsize=7,
                    va="center",
                )

        ax.set_xlabel("Time [s]")
        ax.set_ylabel("LSPR Response [pm]")
        ax.set_title(title, fontsize=10)
        ax.margins(x=0.02)
        fig.tight_layout()
        fig.savefig(dest, dpi=300)
        plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Measure equilibrium step responses in LSPR sensorgrams.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--data", type=Path, default=Path("data"), help="directory of .txt records")
    p.add_argument("--out", type=Path, default=Path("output"), help="output directory")
    p.add_argument("--detect-sigma", type=float, default=3.0,
                   help="Gaussian detection scale [s]; structure below it is noise")
    p.add_argument("--min-prominence", type=float, default=10.0,
                   help="minimum transient prominence, as a multiple of the noise scale")
    p.add_argument("--switch-width", type=float, default=60.0,
                   help="maximum width of a switch transient [s]")
    p.add_argument("--cycle-depth", type=float, default=0.40,
                   help="minimum depth of a regeneration excursion, as a fraction "
                        "of the record's range; these bound the cycles")
    p.add_argument("--guard", type=float, default=25.0,
                   help="guard band excluded either side of the switch [s]")
    p.add_argument("--pre-window", type=float, default=60.0,
                   help="length of the pre-switch fit window [s]")
    p.add_argument("--post-window", type=float, default=250.0,
                   help="maximum length of the relaxation fit window [s]")
    p.add_argument("--min-snr", type=float, default=5.0,
                   help="reject steps below this multiple of the noise scale")
    p.add_argument("--min-step", type=float, default=0.0,
                   help="reject steps below this absolute size [pm]; a stated "
                        "prior on the measurement, disabled by default")
    p.add_argument("--min-tstat", type=float, default=5.0,
                   help="reject steps below this many standard uncertainties")
    args = p.parse_args()

    records = sorted(args.data.glob("*.txt"))
    if not records:
        raise SystemExit(f"No .txt records found in {args.data}/")

    csv_dir = args.out / "csv"
    fit_dir = args.out / "plot_fit"
    plain_dir = args.out / "plot_only"
    for d in (csv_dir, fit_dir, plain_dir):
        d.mkdir(parents=True, exist_ok=True)

    columns = [
        "event", "t_switch_s", "step_pm", "u_pm", "ci95_lo_pm", "ci95_hi_pm",
        "tau_s", "t_stat", "prominence_pm", "width_s", "pre_level_pm",
        "asymptote_pm", "n_pre", "n_post",
    ]

    for path in records:
        t, y = read_record(path)
        results, notes = measure_record(t, y, args)
        name = path.stem

        with open(csv_dir / f"{name}.csv", "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
            for k, r in enumerate(results, start=1):
                writer.writerow([
                    k, f"{r['t_switch']:.2f}", f"{r['step']:.2f}", f"{r['u']:.2f}",
                    f"{r['ci95_lo']:.2f}", f"{r['ci95_hi']:.2f}", f"{r['tau']:.2f}",
                    f"{r['t_stat']:.1f}", f"{r['prominence']:.1f}", f"{r['width']:.1f}",
                    f"{r['pre_level']:.2f}", f"{r['asymptote']:.2f}",
                    r["n_pre"], r["n_post"],
                ])

        plot_record(t, y, results, name, fit_dir / f"{name}.png", plain_dir / f"{name}.png")

        print(f"\n{path}  ({len(t)} samples, dt={np.median(np.diff(t)):.2f} s, "
              f"noise={robust_noise_scale(y):.2f} pm)")
        for k, r in enumerate(results, start=1):
            print(f"  [{k}] t={r['t_switch']:8.1f} s   step = {r['step']:+8.2f} "
                  f"+/- {r['u']:5.2f} pm   95% CI [{r['ci95_lo']:+8.2f}, {r['ci95_hi']:+8.2f}]"
                  f"   tau = {r['tau']:5.1f} s")
        for note in notes:
            print(f"      {note}")
        if not results:
            print("  no measurable events")

    print(f"\nDone. Results in {args.out}/")


if __name__ == "__main__":
    main()
