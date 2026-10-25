"""Charts, tables and an auto-generated investment briefing."""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

INK, MUTED, GRID = "#1f2933", "#7b8794", "#e4e7eb"
BLUE, RED, GREY = "#2563eb", "#dc2626", "#9aa5b1"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.bbox": "tight", "font.size": 9,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "axes.titlesize": 10, "axes.titleweight": "bold",
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "xtick.color": MUTED, "ytick.color": MUTED, "legend.frameon": False,
})


def _save(fig, out, name):
    path = os.path.join(out, name)
    fig.savefig(path)
    plt.close(fig)
    return path


def plot_pri(pri: pd.DataFrame, out: str, highlight=("USA", "GBR", "CAN")) -> str:
    wide = pri["pri"].unstack("country")
    fig, ax = plt.subplots(figsize=(8, 3.2))
    for c in wide.columns:
        if c not in highlight:
            ax.plot(wide.index, wide[c], color=GRID, lw=0.8)
    for c, col in zip(highlight, [BLUE, RED, INK]):
        if c in wide:
            ax.plot(wide.index, wide[c], color=col, lw=1.3, label=c)
    ax.plot(wide.index, wide.mean(axis=1), color=MUTED, lw=1, ls="--", label="Cross-country average")
    ax.set_title("Political Risk Index (standardised, EPU + GPR)")
    ax.set_ylabel("Std. dev. from country mean")
    ax.legend(ncol=4, loc="upper left")
    return _save(fig, out, "fig1_political_risk_index.png")


def plot_lp(lp: pd.DataFrame, out: str) -> str:
    labels = {"xret": "Cumulative excess return vs ACWI (log pts)", "log_rvol": "Log realised volatility"}
    fig, axes = plt.subplots(1, len(labels), figsize=(8, 3))
    for ax, (y, lab) in zip(axes, labels.items()):
        d = lp[lp["outcome"] == y]
        ax.fill_between(d["h"], d["lo90"], d["hi90"], color=BLUE, alpha=0.15, lw=0, label="90% CI")
        ax.plot(d["h"], d["beta"], color=BLUE, lw=1.6, marker="o", ms=3)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_title(lab)
        ax.set_xlabel("Months after a 1 s.d. political-risk shock")
    axes[0].legend(loc="lower left")
    fig.suptitle("Local projections: country and month fixed effects, Driscoll-Kraay SEs", fontsize=9, color=MUTED, y=1.02)
    return _save(fig, out, "fig2_local_projections.png")


def plot_var(var: dict, out: str) -> str:
    cols = var["cols"]
    fig, axes = plt.subplots(1, len(cols) - 1, figsize=(8, 3))
    h = np.arange(var["irf"].shape[0])
    names = {"xret": "Excess return", "log_rvol": "Log realised volatility"}
    for ax, i in zip(axes, range(1, len(cols))):
        ax.fill_between(h, var["lo"][:, i, 0], var["hi"][:, i, 0], color=BLUE, alpha=0.15, lw=0)
        ax.plot(h, var["irf"][:, i, 0], color=BLUE, lw=1.6)
        ax.axhline(0, color=INK, lw=0.7)
        ax.set_title(f"Response of {names.get(cols[i], cols[i])}")
        ax.set_xlabel("Months")
    fig.suptitle(f"Panel VAR({var['p']}) impulse responses to a political-risk shock, 90% country-bootstrap bands",
                 fontsize=9, color=MUTED, y=1.02)
    return _save(fig, out, "fig3_panel_var_irf.png")


def plot_events(per_event: pd.DataFrame, paths: pd.DataFrame, out: str) -> str:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6), gridspec_kw={"width_ratios": [1.1, 1]})
    d = per_event.sort_values("CAR [0,+5]")
    colors = [RED if p < 0.05 else GREY for p in d["p [0,+5]"]]
    a1.barh(d["country"] + ": " + d["event"].str.slice(0, 26), d["CAR [0,+5]"] * 100, color=colors)
    a1.axvline(0, color=INK, lw=0.7)
    a1.set_title("CAR [0,+5] by event (red: p < 0.05)")
    a1.set_xlabel("% vs market model")
    a1.tick_params(axis="y", labelsize=6)
    a1.grid(axis="y", visible=False)
    for col in paths.columns:
        a2.plot(paths.index, paths[col] * 100, color=GRID, lw=0.7)
    a2.plot(paths.index, paths.mean(axis=1) * 100, color=BLUE, lw=2, label="Average across events")
    a2.axvline(0, color=INK, lw=0.7, ls=":")
    a2.axhline(0, color=INK, lw=0.7)
    a2.set_title("Average cumulative abnormal return")
    a2.set_xlabel("Trading days from event")
    a2.set_ylabel("%")
    a2.legend(loc="lower left")
    return _save(fig, out, "fig4_event_study.png")


def plot_regimes(reg: pd.DataFrame, out: str) -> str:
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8, 3))
    a1.bar(reg.index.astype(str), reg["ann. excess return"] * 100, color=[BLUE, GREY, RED])
    a1.axhline(0, color=INK, lw=0.7)
    a1.set_title("Next-month excess return vs ACWI (ann., %)")
    a2.bar(reg.index.astype(str), reg["avg realised vol"] * 100, color=[BLUE, GREY, RED])
    a2.set_title("Next-month realised volatility (%)")
    fig.suptitle("Country outcomes by political-risk tercile (real-time index, ranked within month)",
                 fontsize=9, color=MUTED, y=1.02)
    return _save(fig, out, "fig5_regimes.png")


def plot_backtest(rets: pd.DataFrame, out: str) -> str:
    cum = rets.cumsum()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 4.4), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
    for col, c in zip(rets.columns, [GREY, BLUE]):
        a1.plot(cum.index, np.exp(cum[col]) * 100, color=c, lw=1.4, label=col)
        a2.plot(cum.index, (np.exp(cum[col] - cum[col].cummax()) - 1) * 100, color=c, lw=1)
    a1.set_title("Political-risk tilt vs equal-weight country portfolio (growth of 100, USD)")
    a1.legend(loc="upper left")
    a2.set_title("Drawdown (%)")
    return _save(fig, out, "fig6_backtest.png")


def plot_stress(stress: pd.DataFrame, out: str) -> str:
    d = stress.drop(columns=["BENCH"], errors="ignore") * 100
    fig, ax = plt.subplots(figsize=(8, 0.5 + 0.45 * len(d)))
    vmax = np.nanmax(np.abs(d.values))
    im = ax.imshow(d.values, cmap="RdBu", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_xticks(range(d.shape[1]), d.columns, rotation=45, ha="right")
    ax.set_yticks(range(d.shape[0]), d.index)
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            v = d.values[i, j]
            if np.isfinite(v):
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=7,
                        color="white" if abs(v) > vmax * 0.6 else INK)
    ax.grid(False)
    ax.set_title("Cumulative USD return during political-stress windows (%)")
    fig.colorbar(im, ax=ax, shrink=0.8)
    return _save(fig, out, "fig7_stress_tests.png")


# --- Briefing -------------------------------------------------------------------------------
def _fmt_pct(x, d=1):
    return "n/a" if pd.isna(x) else f"{x * 100:.{d}f}%"


def briefing(res: dict, out: str, synthetic: bool) -> str:
    lp, reg, m, summ, per_event, stress, w = (res[k] for k in ["lp", "regimes", "metrics", "event_summary",
                                                               "per_event", "stress", "weights"])
    r3 = lp[(lp.outcome == "xret") & (lp.h == 3)].iloc[0]
    v1 = lp[(lp.outcome == "log_rvol") & (lp.h == 1)].iloc[0]
    allev = summ.loc["All events"]
    tilt, eq = m.loc["Political-risk tilt"], m.loc["Equal weight"]
    worst = per_event.nsmallest(3, "CAR [0,+5]")
    sig = lambda p: "statistically significant" if p < 0.05 else "not statistically significant"  # noqa: E731

    lines = [
        "# Investment Briefing: Political Risk and the Global Equity Mix", "",
    ]
    if synthetic:
        lines += ["> **Synthetic data.** These numbers come from simulated data with a known effect built in, "
                  "to check that the pipeline works. They are not findings. Run `python run_analysis.py` "
                  "with internet access for real results.", ""]
    lines += [
        f"Coverage: {res['n_countries']} equity markets, {res['start']} to {res['end']}, monthly. "
        f"Political Risk Index (PRI) combines Economic Policy Uncertainty and Geopolitical Risk "
        f"(PCA weights: EPU {res['pca'].iloc[0]:.2f}, GPR {res['pca'].iloc[1]:.2f}).", "",
        "## Key findings", "",
        f"1. **Return impact.** A one-standard-deviation surprise in a country's political risk is followed by a "
        f"cumulative {r3.beta * 100:+.2f} pp excess return versus ACWI over four months (t+0 to t+3; "
        f"p = {r3.pval:.2f}, {sig(r3.pval)}). Month fixed effects remove global moves, "
        f"so this is the country-specific effect.",
        f"2. **Volatility impact.** The same shock moves next-month realised volatility by "
        f"{(np.exp(v1.beta) - 1) * 100:+.1f}% (p = {v1.pval:.2f}).",
        f"3. **Regimes.** Countries in the top third of political risk returned "
        f"{_fmt_pct(reg.attrs['high_minus_low_ann'])} a year relative to the bottom third the following month "
        f"(p = {reg.attrs['p']:.2f}), with average realised volatility of "
        f"{_fmt_pct(reg.loc['High risk', 'avg realised vol'])} vs {_fmt_pct(reg.loc['Low risk', 'avg realised vol'])}.",
        f"4. **Event risk.** Across {int(allev['n_events'])} political events, the mean abnormal return over "
        f"[0,+5] days was {_fmt_pct(allev['mean CAR [0,+5]'], 2)} (BMP p = {allev['BMP p [0,+5]']:.2f}). "
        f"Largest moves: " + "; ".join(f"{r.country} {r.event} {_fmt_pct(r['CAR [0,+5]'])}" for _, r in worst.iterrows()) + ".",
        f"5. **Portfolio tilt.** Underweighting the three markets with the sharpest rise in real-time political risk "
        f"gave a return/volatility ratio of {tilt['return/vol']:.2f} vs {eq['return/vol']:.2f} for equal weight, "
        f"a max drawdown of {_fmt_pct(tilt['max drawdown'])} vs {_fmt_pct(eq['max drawdown'])}, tracking error of "
        f"{_fmt_pct(tilt['tracking error'])} and an information ratio of {tilt['information ratio']:.2f}.",
        "",
        "## Implications for the total fund", "",
        "- Political risk is better treated as a **risk-budget input** (position sizing and hedging around known "
        "events) than as a standalone return signal; the evidence for lasting return effects should be judged on "
        "the significance figures above, not the point estimates.",
        "- By event type, the largest average [0,+5] reaction was for **"
        + (kinds := summ.drop(index="All events")["mean CAR [0,+5]"]).idxmin().replace("_", " ")
        + f"** events ({_fmt_pct(kinds.min(), 2)}) and the smallest for **"
        + kinds.idxmax().replace("_", " ") + f"** ({_fmt_pct(kinds.max(), 2)}). Scheduled elections give "
        "time to hedge ahead of the vote; unscheduled shocks do not.",
        "- Stress-test returns are in USD and so include currency moves. For a Canadian-dollar fund, the "
        "FX hedging decision is part of the political-risk exposure, not separate from it.",
        "",
        "## Current read (latest month)", "",
    ]
    latest = res["pri_latest"].sort_values(ascending=False)
    lines += ["| Country | PRI (real time) | Model weight |", "|---|---|---|"]
    for c, v in latest.items():
        lines.append(f"| {c} | {v:+.2f} | {_fmt_pct(w.iloc[-1].get(c, np.nan))} |")
    lines += ["", "## Stress tests (cumulative USD return)", "", (stress * 100).round(1).to_markdown(), "",
              "## Method notes and limitations", "",
              "- PRI uses within-country z-scores; `pri_rt` uses expanding windows so the backtest has no look-ahead.",
              "- Local projections include two lags of the outcome and the shock; Driscoll-Kraay errors allow for "
              "cross-country and serial correlation.",
              "- Panel VAR is identified with political risk ordered first; results may depend on this ordering.",
              "- Ten markets and roughly two decades of data limit statistical power. Treat estimates as indicative.",
              "- Event dates are compiled by the author and should be checked before use.", ""]
    path = os.path.join(out, "briefing.md")
    with open(path, "w") as f:
        f.write("\n".join(lines))
    return path
