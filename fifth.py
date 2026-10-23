import argparse
import os
import sys
from csv import reader

from margins import HEADER, format_row, margin_row, non_negative_int, write_lines


def build_parser():
    p = argparse.ArgumentParser(description="Recompute the margin CSV from an existing main.py output CSV "
                                            "(columns name,last,low,high,...; only the first four are read).")
    p.add_argument('--input', metavar='PATH', default='./half.csv',
                   help='input CSV, e.g. the output of main.py (default: %(default)s)')
    p.add_argument('--output', metavar='PATH', default='./fifi.csv',
                   help='output CSV, must differ from --input (default: %(default)s)')
    p.add_argument('--coef', type=non_negative_int, metavar='N', default=5,
                   help="1/N of the day's range, N>=0 (default: %(default)s)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    if os.path.realpath(args.input) == os.path.realpath(args.output):
        sys.exit("error: --input and --output must differ")
    try:
        with open(args.input, newline='') as f:
            rows = [r for r in reader(f) if r and r[:4] != ["name", "last", "low", "high"]]
    except FileNotFoundError:
        sys.exit(f"error: {args.input} not found; run `python main.py` first or pass --input PATH")
    # main.py writes %f (6 decimals), so recomputing from its CSV can differ for tiny prices
    try:
        lines = [HEADER + "\n"] + [
            format_row(r[0], margin_row(float(r[1]), float(r[2]), float(r[3]), args.coef)) for r in rows]
    except (IndexError, ValueError) as exc:
        sys.exit(f"error: malformed input row ({type(exc).__name__}: {exc})")
    write_lines(args.output, lines)


if __name__ == "__main__":
    main()
