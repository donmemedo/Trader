# HANDOFF - Trader hardening pass

Branch: `fix/harden-trader-scripts`. Chronological record and verification evidence: `docs/LAST_Report.md`.

## P0 - action required from the repo owner (code cannot do this)

A CoinEx API access id + secret were hardcoded in `main.py`, and are present in every commit that contains that
file (since 2022-05-23). The repository is **public** (checked with `gh repo view`). This change removes them from the working tree
only: they remain in git history, forks, clones and caches. **Treat the key pair as compromised.** Merging this
change does not end the exposure; only revoking the key does.

In this order:

1. **Export evidence first**: the key's permissions, IP allow-list and access/trade/withdrawal history from CoinEx.
2. **Delete (not just disable) the key.** Do not replace it: the ticker call is believed to need no key.
3. If it had trade or withdraw permission, or shows use from unknown IPs, treat it as an incident (CoinEx
   support, 2FA, withdrawal-address whitelist).
4. **Search for the same pair elsewhere**: other repos, crontabs, shell history, CI secrets, other machines.
5. Confirm who owns the CoinEx account (the repo owner and the local git user differ) and tell them.
6. Enable GitHub secret scanning + push protection (free on public repos). CoinEx is unlikely to be a built-in
   partner pattern, so also add a local scan (see Follow-ups).
7. Rewriting history (`git filter-repo` + force-push) or making the repo private is optional and cosmetic: it
   does not reach forks or cached copies. Nothing was rewritten here; that decision is yours.

## What changed

| Area | Change |
|---|---|
| Secrets | Hardcoded credentials removed. Optional env vars `COINEX_ACCESS_ID` / `COINEX_SECRET_KEY`. `--user`/`--password` are refused with an error that does not echo the value (an old wrapper would otherwise leak its key into cron mail/logs) - **breaking** for anything still passing them. Error messages redact env values (longest first). |
| `margins.py` (new) | One shared margin function replacing five copy-pasted loops in `main.py` and the duplicate math in `fifth.py`. Output is byte-identical to the original (golden-tested), including `nan`/`inf` rows. |
| `main.py` | Importable (`main()` + `__main__` guard). Computes every row **before** opening any file, so a malformed ticker no longer leaves partial CSVs (the original already fetched before opening files, but parsed while writing). `--help` fixed: bare `%` in the help text crashed `--help` on Python 3.12 and the parser build itself on 3.14. One stderr summary line. Negative `--coef` rejected (0 still accepted, as before). LF line endings on every OS (the original wrote CRLF on Windows). |
| `fifth.py` | No longer crashes on the header row of `main.py`'s own CSV. `with` file handling. Refuses `--input == --output` (it used to truncate its own input). Friendly missing-file message. |
| Tests | `tests/` + `pytest.ini`: golden parity against the original code, unit tests, header regression, guards, secret-pattern scan, a strict `xfail` for the known `comp.py` bug. |
| Housekeeping | `requirements.txt`, `requirements-dev.txt`, README rewrite, `.gitignore` additions, `.gitattributes` (fixtures are byte-compared). |

Untouched on purpose: `comp.py`, `tr.py`.

## Decisions that are yours (default taken in brackets)

| # | Question | Default taken |
|---|---|---|
| 1 | What is the real `coinex` client? `from coinex.coinex import CoinEx` does **not** resolve against PyPI `coinex` 0.1.0 (it ships no `coinex.coinex` module). `requirements.txt` lists numpy only. [CONFLICT] | Left unresolved; README warns not to `pip install coinex` expecting the client. No guessed pin. |
| 2 | Replace the SDK with a stdlib `urllib` GET of the public ticker endpoint (removes the unvetted dependency and the credential need)? Needs a live-API check and a look at v1 deprecation. | Not done; recommended. |
| 3 | What produces `comp.py`'s 13-column headerless input? Nothing in this repo does, and it caps at 1000 rows (`IndexError` on row 1001). | Unchanged; documented; a strict `xfail` test pins the bug. |
| 4 | `tr.py` is a hardcoded, defective duplicate of `comp.py` (aliased `[[0]*7]*1000` rows, string comparisons). Delete it? | Left in place, marked legacy in the README. |
| 5 | `nan`/`inf` rows for zero-range / zero-low coins are written as before (a financial-output behavior). | Preserved; counted in the stderr summary. |

## Known, accepted low risks (found by the red-team probes; none Medium/High)

- Output files are written with `open(..., "w")`: they follow symlinks, and a failure part-way through the five
  writes can leave the set inconsistent. Same as the original. Fix if needed: temp file + `os.replace`.
- The `name` column is written unquoted (`%s`): a name with commas/newlines, or starting with `=+-@`, passes through
  (CSV/formula injection when opened in a spreadsheet). Names come from the exchange list or your own CSV.
- Secret redaction is exact-substring only (a URL-encoded or re-encoded secret would not be masked).
- A huge `--coef` (`10**400`) overflows: `main.py` reports it as "malformed ticker data (OverflowError ...)", which
  is a misleading message, and `fifth.py` prints a traceback. A directory or binary file as `fifth.py` input also
  gives a traceback. None of these damage state (nothing is written).

## Follow-ups (not in this change)

- Secret scan in pre-commit + one CI job (`fetch-depth: 0`, e.g. gitleaks with a `[0-9A-Fa-f]{32,48}` rule).
  bandit, ruff `S` and semgrep `p/secrets` all **missed** the original leak (it sat in an argparse default).
  After rotation, baseline the old commits so CI does not fail forever.
- Optional `ci.yml` running `pytest` on the supported Python versions and a weekly `pip-audit -r requirements.txt`.
- Pin the `coinex` client by version + hash once identified.

## Not done / out of scope

- No FastAPI/Next.js web app, Docker Compose, PWA/APK/IPA: this repo is four CLI scripts and nothing in the
  request or repo documents calls for a web product. Persian/RTL/dark-mode requirements apply to a web UI only.
- No history rewrite, no key rotation (owner actions above).
