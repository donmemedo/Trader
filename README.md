# Trader

Small scripts around CoinEx market tickers: for every coin, work out a buy and a sell price inside the
day's low-high range, at several margins (1/2, 1/3, 1/4, 1/5 and a custom 1/N of the range).

## Install

Python 3.10 or newer (the code uses `zip(strict=True)`); tested on 3.12 and 3.14.

```
pip install -r requirements.txt
```

**The `coinex` client library is unresolved.** `main.py` does `from coinex.coinex import CoinEx`, but the
provider of that module is not identified: the PyPI package `coinex` 0.1.0 does not contain a `coinex.coinex`
module, so it is deliberately not pinned in `requirements.txt`. **Do not `pip install coinex` expecting the
client**: anyone can publish a new version under that name, and the client receives your API credentials if you
set any. Get the client only from a source you have audited, and pin it by version and hash. Until then
`main.py` exits with a "could not import the `coinex` client library" error. The tests do not need it (they use
a stub).

## Credentials

The ticker endpoint is believed to be public, so credentials are optional. If the API turns out to require
them, set them in the environment (never on the command line):

```
export COINEX_ACCESS_ID=...
export COINEX_SECRET_KEY=...
```

Use a read-only key with no withdrawal permission.

**Breaking change:** `--user` and `--password` were removed from `main.py` (they put secrets on the
command line and in the source). Cron jobs or wrapper scripts that still pass them now fail with an error
that does not repeat the value; switch them to the env vars.
Also, `--coef` now rejects negative numbers (0 is still accepted).

## Usage

Run order: `main.py` -> `fifth.py`. `comp.py` compares two snapshot CSVs in a different 13-column format
(see Known limitations); it does not consume `main.py`'s output directly.

```
python main.py                       # half.csv third.csv quarter.csv fifth.csv + Custom_Margin.csv in the cwd
python main.py --coef 8 --half half_custom.csv
python fifth.py --input half.csv --output fifi.csv --coef 5
python comp.py --yesterday a.csv --today b.csv
```

`main.py` fetches the tickers and computes all five files before writing anything, so a failed fetch or a
malformed ticker never truncates existing CSVs. An I/O error *while writing* (for example a missing output
directory for a later path) can still leave the set partly written: create output directories first.
`fifth.py` recomputes a margin from an existing CSV (columns 1-4: name, last, low, high; a header row is
skipped) and refuses `--input` equal to `--output`.
Note `main.py` writes values with 6 decimals (`%f`), so recomputing from its CSV can differ from `main.py`
for tiny prices. Output files use LF line endings on every OS (the original wrote CRLF on Windows).

### CSV columns

| column | meaning |
| --- | --- |
| name | market, e.g. `BTCUSDT` |
| last, low, high | last / 24h low / 24h high price |
| profit | (high - low) / low, a fraction |
| tempbuy, tempsell | (1 -/+ profit/N) * last, price before clamping to the range |
| buy, sell | tempbuy clamped up to low, tempsell clamped down to high, price |
| myprofit | 100 * (sell - buy) / buy, percent |
| Ratio | myprofit / profit |

`nan` and `inf` appear for zero-range or zero-low coins (division by zero). That is preserved on purpose, so
the output stays byte-identical to the original script. NumPy's divide-by-zero warnings are suppressed;
instead `main.py` prints one stderr line with the number of rows that have a non-finite Ratio (the maximum
over the five files).

## Tests

```
pip install -r requirements-dev.txt
pytest
```

No network is used and the real `coinex` library is never imported. The golden CSVs in `tests/fixtures/`
were produced by the original `main.py` against fabricated tickers; the `{"ticker": {...}}` response shape
is assumed from the original code.

## Known limitations

- `comp.py` needs a 13-column headerless input that nothing in this repo produces, and it caps input at
  1000 rows (an `IndexError` beyond that; covered by a strict xfail test).
- `tr.py` is legacy and defective (aliased `[[0]*7]*1000` rows, string comparisons). Do not use it.

## Security

An API key pair that was hardcoded in `main.py` is still present in this repository's public git history.
Removing it from the code does not un-leak it: it **must be revoked at CoinEx**. (Update this note once that
is done.)
