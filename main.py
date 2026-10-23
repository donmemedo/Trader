import argparse
import os
import sys

from margins import csv_lines, non_negative_int, write_lines


class _Removed(argparse.Action):
    """--user/--password are gone: refuse without echoing the value, which would reach logs and cron mail."""

    def __call__(self, parser, namespace, values, option_string=None):
        parser.error(f"{option_string} was removed; set COINEX_ACCESS_ID and COINEX_SECRET_KEY instead")


def build_parser():
    p = argparse.ArgumentParser(description="Fetch all CoinEx tickers and write buy/sell margin CSVs.")
    for flag in ('--user', '--password'):
        p.add_argument(flag, action=_Removed, help=argparse.SUPPRESS)
    p.add_argument('--half', metavar='PATH', default='./half.csv',
                   help='output CSV for the 1/2 (50%%) margin (default: %(default)s)')
    p.add_argument('--third', metavar='PATH', default='./third.csv',
                   help='output CSV for the 1/3 (33%%) margin (default: %(default)s)')
    p.add_argument('--quarter', metavar='PATH', default='./quarter.csv',
                   help='output CSV for the 1/4 (25%%) margin (default: %(default)s)')
    p.add_argument('--fifth', metavar='PATH', default='./fifth.csv',
                   help='output CSV for the 1/5 (20%%) margin (default: %(default)s)')
    p.add_argument('--coef', type=non_negative_int, metavar='N', default=10,
                   help="custom margin: 1/N of the day's range, N>=0, written to ./Custom_Margin.csv "
                        "(default: %(default)s)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    # optional: the ticker endpoint is believed public; never pass secrets on the command line
    keys = [os.environ.get(k, "") for k in ("COINEX_ACCESS_ID", "COINEX_SECRET_KEY")]
    try:
        from coinex.coinex import CoinEx
    except ImportError as exc:
        sys.exit(f"error: could not import the `coinex` client library ({exc}); see README")
    try:
        coins = CoinEx(*keys).market_ticker_all()["ticker"]
    except Exception as exc:
        msg = str(exc)
        for k in sorted(filter(None, keys), key=len, reverse=True):  # longest first: one value may contain the other
            msg = msg.replace(k, "***")
        raise SystemExit(f"error: could not fetch tickers ({type(exc).__name__}: {msg}); "
                         "if the API requires auth set COINEX_ACCESS_ID and COINEX_SECRET_KEY") from None
    # compute everything before touching any file, so a bad ticker never truncates old CSVs
    try:
        sets = [csv_lines(coins, d) for d in (2, 3, 4, 5, args.coef)]
    except (KeyError, ValueError, TypeError, OverflowError) as exc:
        sys.exit(f"error: malformed ticker data ({type(exc).__name__}: {exc})")
    print("Custom Margin is  1/%d\n" % args.coef)
    paths = (args.half, args.third, args.quarter, args.fifth, 'Custom_Margin.csv')
    for path, (lines, _) in zip(paths, sets, strict=True):
        write_lines(path, lines)
    print(f"wrote {len(coins)} coins x 5 files; up to {max(bad for _, bad in sets)} with non-finite ratio per file",
          file=sys.stderr)


if __name__ == "__main__":
    main()
