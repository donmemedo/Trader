import argparse

import numpy as np

HEADER = "name,last,low,high,buy,sell,profit,tempbuy,tempsell,myprofit,Ratio"
ROW = "%s" + ",%f" * 10 + "\n"


def margin_row(last, low, high, divisor):
    """-> (last, low, high, buy, sell, profit, tempbuy, tempsell, myprofit, ratio).

    Zero-range / zero-low coins give nan/inf on purpose (numpy scalars, no ZeroDivisionError).
    The builtin max/min argument order decides the nan results: keep it.
    """
    last, low, high = np.float64(last), np.float64(low), np.float64(high)
    with np.errstate(all="ignore"):
        profit = (high - low) / low
        tb = (1 - profit / divisor) * last
        ts = (1 + profit / divisor) * last
        buy = max(tb, low)
        sell = min(ts, high)
        myprofit = 100 * (sell - buy) / buy
        ratio = myprofit / profit
    return last, low, high, buy, sell, profit, tb, ts, myprofit, ratio


def format_row(name, row):
    return ROW % (name, *row)


def csv_lines(coins, divisor):
    """{name: {"last","low","high"}} -> (HEADER + one line per coin, count of non-finite ratios)."""
    lines, bad = [HEADER + "\n"], 0
    for name, c in coins.items():
        row = margin_row(float(c["last"]), float(c["low"]), float(c["high"]), divisor)
        bad += not np.isfinite(row[-1])
        lines.append(format_row(name, row))
    return lines, bad


def write_lines(path, lines):
    with open(path, "w", newline="\n") as f:
        f.writelines(lines)


def non_negative_int(s):
    n = int(s)
    if n < 0:
        raise argparse.ArgumentTypeError(f"{s!r} must be >= 0")
    return n
