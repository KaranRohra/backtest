"""Run one backtest end to end.

    python run.py E01_2026-10-27_Name [--no-video]      (folder inside backtests/)

Reads backtests/<name>/config.json + strategy.py, pulls candles through the shared
cache (data/), and writes results/, a scoreboard row and the README leaderboard.
If the (private) Remotion project is present it also renders the comparison video.
"""
import argparse
import importlib.util
import json
from datetime import date, timedelta

import pandas as pd

from core.datastore import get_candles
from core.engine import Settings, backtest, benchmark, stats, verdict
from core.paths import ROOT

SCOREBOARD = ROOT / "scoreboard.csv"
README = ROOT / "README.md"
BACKTESTS = ROOT / "backtests"
VERDICT_ICON = {"WORKS": "✅ Works", "MIXED": "⚠️ Mixed", "FAILS": "❌ Fails"}


def load_strategy(ep):
    spec = importlib.util.spec_from_file_location(f"{ep.name}.strategy", ep / "strategy.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def window(cfg):
    end = pd.Timestamp(cfg.get("end") or date.today() - timedelta(days=1))
    start = pd.Timestamp(cfg["start"]) if cfg.get("start") else end - pd.DateOffset(months=int(cfg.get("years", 3) * 12))
    return start, end


def sensitivity(data, strat, params, settings, start, grid):
    """One parameter at a time, the rest at their defaults."""
    rows = []
    for name, values in grid.items():
        for v in values:
            t, eq = backtest(data, strat, {**params, name: v}, settings, start)
            st = stats(t, eq)
            rows.append({"param": name, "value": v, "default": params.get(name) == v,
                         **{k: st.get(k) for k in ("total_return_pct", "cagr_pct", "max_drawdown_pct",
                                                   "profit_factor", "win_rate_pct", "n_trades", "avg_r")}})
    return pd.DataFrame(rows)


def update_scoreboard(ep, cfg, symbols, tag, st, v):
    row = {"episode": ep.name + (f" [{tag}]" if tag else ""), "strategy": cfg["title"],
           "creator": cfg.get("creator", ""), "symbols": " ".join(symbols), "interval": cfg.get("timeframe_label", cfg["interval"]), "period": f"{st['start']}..{st['end']}",
           "trades": st["n_trades"], "win_rate_pct": round(st.get("win_rate_pct", 0), 1),
           "profit_factor": round(st.get("profit_factor", 0), 2), "return_pct": round(st["total_return_pct"], 1),
           "cagr_pct": round(st["cagr_pct"], 1), "max_dd_pct": round(st["max_drawdown_pct"], 1),
           "bh_return_pct": round(st.get("bh_total_return_pct", 0), 1), "verdict": v}
    sb = pd.read_csv(SCOREBOARD) if SCOREBOARD.exists() else pd.DataFrame(columns=list(row))
    sb = pd.concat([sb[sb.episode != row["episode"]], pd.DataFrame([row])]).sort_values("episode")
    sb.to_csv(SCOREBOARD, index=False)
    update_leaderboard(sb)


def update_leaderboard(sb):
    """Rewrite the table between the leaderboard markers in README.md from scoreboard.csv."""
    start, end = "<!-- leaderboard:start -->", "<!-- leaderboard:end -->"
    text = README.read_text() if README.exists() else ""
    if start not in text or end not in text:
        return
    lines = ["| # | Strategy | Creator | Market | Trades | Win rate | Profit factor | Return | Buy & hold | Max DD | Verdict |",
             "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in sb.itertuples():
        folder = r.episode.split(" [")[0]
        market = " ".join(s.split(":", 1)[-1] for s in r.symbols.split(" NSE:")).replace("XAUUSD", "Gold (XAUUSD)")
        tf = {"minute": "1-min", "day": "daily"}.get(r.interval, r.interval)
        lines.append(f"| {folder.split('_')[0]} | [{r.strategy}](backtests/{folder}) | {r.creator} | {market} · {tf} | "
                     f"{r.trades} | {int(r.win_rate_pct + 0.5)}% | {r.profit_factor:.2f} | {r.return_pct:+.1f}% | "
                     f"{r.bh_return_pct:+.1f}% | {r.max_dd_pct:.1f}% | {VERDICT_ICON.get(r.verdict, r.verdict)} |")
    head, rest = text.split(start, 1)
    README.write_text(head + start + "\n" + "\n".join(lines) + "\n" + end + rest.split(end, 1)[1])


def run_one(ep, cfg, strat, symbols, tag):
    """One backtest over `symbols`; outputs go to results/<tag>/. Returns what the video needs."""
    # per-symbol overrides, e.g. {"overrides": {"DUKAS:XAUUSD": {"params": {...}, "settings": {...}, "grid": {...}}}}
    ov = cfg.get("overrides", {}).get(symbols[0], {}) if len(symbols) == 1 else {}
    params = {**getattr(strat, "PARAMS", {}), **cfg.get("params", {}), **ov.get("params", {})}
    settings = Settings(**{**cfg.get("settings", {}), **ov.get("settings", {})})
    grid = ov.get("grid", cfg.get("grid"))
    start, end = window(cfg)
    fetch_from = start - timedelta(days=cfg.get("warmup_days", 0))

    data = {s: get_candles(s, cfg["interval"], fetch_from, end) for s in symbols}
    bsym = symbols[0] if tag else cfg.get("benchmark", symbols[0])
    bdf = data.get(bsym) if bsym in data else get_candles(bsym, cfg["interval"], fetch_from, end)

    trades, eq = backtest(data, strat, params, settings, start)
    bh = benchmark(bdf.loc[start:], settings.capital)
    full = stats(trades, eq, bh)

    split = end - pd.DateOffset(months=cfg.get("oos_months", 12))
    ins = stats(trades[trades.entry_time < split] if len(trades) else trades, eq.loc[:split], bh)
    oos = stats(trades[trades.entry_time >= split] if len(trades) else trades, eq.loc[split:], bh)
    v, reasons = verdict(full, oos)

    sub = tag or ""
    res = ep / "results" / sub
    res.mkdir(parents=True, exist_ok=True)
    out = {"verdict": v, "reasons": reasons, "symbols": symbols, "params": params, "settings": settings.__dict__,
           "costs": "zero (before costs)", "full": full, "in_sample": ins, "out_of_sample": oos,
           "split_date": str(split.date())}
    (res / "stats.json").write_text(json.dumps(out, indent=1, default=str))
    trades.to_csv(res / "trades.csv", index=False)
    daily = lambda x: x.resample("D").last().dropna()  # noqa: E731 - keep csv small for intraday data
    pd.concat([daily(eq), daily(bh)], axis=1).ffill().to_csv(res / "equity.csv")
    if grid:
        sens = sensitivity(data, strat, params, settings, start, grid)
        sens.to_csv(res / "sensitivity.csv", index=False)

    names = ", ".join(s.split(":")[1] for s in symbols)

    md = [f"# {cfg['title']} — {names} — {v}", "", *[f"- {r}" for r in reasons], "",
          f"Period {full['start']} → {full['end']} · {cfg['interval']} · **before costs** · OOS from {split.date()}",
          "", "| Metric | Full | In-sample | Out-of-sample | Buy & hold |", "|---|---|---|---|---|"]
    for k, label in [("total_return_pct", "Return %"), ("cagr_pct", "CAGR %"), ("max_drawdown_pct", "Max DD %"),
                     ("n_trades", "Trades"), ("win_rate_pct", "Win rate %"), ("profit_factor", "Profit factor"),
                     ("expectancy_pct", "Avg trade %"), ("avg_r", "Avg R"), ("total_r", "Total R"),
                     ("max_consecutive_losses", "Max losing streak"), ("sharpe", "Sharpe")]:
        bhk = {"total_return_pct": "bh_total_return_pct", "cagr_pct": "bh_cagr_pct",
               "max_drawdown_pct": "bh_max_drawdown_pct"}.get(k)
        cells = [full.get(k), ins.get(k), oos.get(k), full.get(bhk) if bhk else None]
        if all(c is None for c in cells):
            continue
        md.append(f"| {label} | " + " | ".join("–" if c is None else f"{c:.2f}" if isinstance(c, float) else str(c)
                                                for c in cells) + " |")
    if full.get("exit_reasons"):
        md += ["", "Exits: " + ", ".join(f"{k} {n}" for k, n in full["exit_reasons"].items())]
    if grid:
        md += ["", "## Parameter sensitivity (one at a time)", "", sens.round(2).to_markdown(index=False)]
    (res / "summary.md").write_text("\n".join(md) + "\n")
    update_scoreboard(ep, cfg, symbols, tag, full, v)
    print("\n".join(md), "\n")
    return {"name": names, "symbols": symbols, "eq": eq, "bh": bh, "stats": full, "verdict": v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("episode")
    ap.add_argument("--no-video", action="store_true")
    a = ap.parse_args()
    ep = next(p for p in (BACKTESTS / a.episode, ROOT / a.episode) if p.exists()).resolve()
    cfg = json.loads((ep / "config.json").read_text())
    if not (cfg.get("start") and cfg.get("end")):  # pin the window on first run so published results stay reproducible
        start, end = window(cfg)
        cfg = {**cfg, "start": f"{start:%Y-%m-%d}", "end": f"{end:%Y-%m-%d}"}
        (ep / "config.json").write_text(json.dumps(cfg, indent=2) + "\n")
    strat = load_strategy(ep)
    if cfg.get("separate"):  # each symbol is its own backtest; the video compares them
        results = [run_one(ep, cfg, strat, [s], s.split(":")[1].replace(" ", "_")) for s in cfg["symbols"]]
    else:
        results = [run_one(ep, cfg, strat, cfg["symbols"], None)]
    if not a.no_video and (ROOT / "remotion").exists():
        from core import video  # channel video tooling; not part of the public repo

        video.render(ep, video.build_props(ep, cfg, results))


if __name__ == "__main__":
    main()
