# LAST_Report - Trader hardening pass

Branch `fix/harden-trader-scripts`. Companion: `HANDOFF.md` (owner actions, decisions, follow-ups).
Every result below was observed in this session; anything not run is listed under "Not run / unresolved".
`$SCRATCH` is the session's scratch directory outside the repository (isolated venvs, stubs, scan copies).

## 1. Outcome in one paragraph

The repo is four flat Python CLI scripts for the CoinEx exchange, not a web application, so no FastAPI/Next.js
app was built (nothing in the request or repo calls for one). A hardcoded exchange API key pair in `main.py`
(present in every commit that contains the file, since 2022-05-23; repo is public) was removed from the working tree; **it stays in public git
history and must be revoked by the owner**. Three functional bugs were reproduced and fixed, the duplicated margin
math was folded into one tested module, and the output CSVs are byte-identical to the original program's.
57 tests pass (+1 strict xfail documenting a known bug) on Python 3.12 and 3.14.

## 2. Scope decisions and assumptions

| Decision | Why |
|---|---|
| No FastAPI/Next.js, Docker Compose, PWA/APK/IPA, EN/FA, RTL, dark mode | Those apply to a web product. The prompt says to follow the repo's own specification and not force a framework. The repo's only spec is the 2-line README ("Coinex Trades"). |
| No Rust work | No `product-source-code/` directory and no Rust. |
| `comp.py`, `tr.py` unchanged | `comp.py` needs a 13-column headerless input that nothing in this repo produces; `tr.py` is a defective duplicate. Changing code whose contract is unknown risks a confident wrong fix. |
| `coinex` dependency left unresolved | PyPI `coinex` 0.1.0 ships no `coinex.coinex` module (inspected without executing it). No guessed pin. |
| `nan`/`inf` output preserved | Output contract of the original program; counted in a stderr summary instead of changed. |
| Credentials optional via env, not required | The ticker endpoint is believed public and the SDK constructor is unverified; requiring them would be a speculative requirement. |
| Pre-existing untracked bootstrap files (`.claude/`, `CLAUDE.md`, `docs/*` except this report, `scripts/`, `setup-claude-project.sh`) not committed | Not part of this task; `.claude/settings.json` declares a hook and a plugin marketplace and must not ride along in a public PR. |

## 3. Chronology

1. Read repo state: 6 commits (the key enters at the second, same day as the root commit), only product code is `main.py`, `fifth.py`, `comp.py`, `tr.py`; untracked bootstrap files; `gh` authenticated, remote `origin`, repo visibility PUBLIC.
2. Ran `/graphify .` (partial, see ledger), `/ponytail:ponytail`, `/ponytail-review`.
3. Reproduced defects in isolated venvs (system Python has no numpy): `fifth.py` ValueError on `main.py`'s own header row; `comp.py` IndexError at row 1001; zero-range coins produce `nan` silently; `--help` crash from bare `%` in help text (3.12: on `--help`; 3.14: at parser build).
4. Inspected the `coinex` PyPI package without executing it: no `coinex.coinex` module.
5. Captured byte-exact golden CSVs from the **original** `main.py` run against a stub client (12 fabricated tickers, `--coef 1` and `10`).
6. `triage` -> `build` / high risk / `blue-team-lead` after build. Ten advisory agents reviewed the plan; their conflicts were resolved on evidence (section 6).
7. `build` worker implemented the spec; I re-ran its claims independently and read all code.
8. Seven post-implementation reviewers (red/blue/audit/sweep/builder) ran against the real code; accepted fixes applied and mutation-checked (section 6).
9. Final scans, graph refresh, `verifier` pass, then explicit-path commit, push, PR.

## 4. Findings (all reproduced or read in code)

| ID | Severity | Finding | Status |
|---|---|---|---|
| F1 | **High** (pre-existing) | API access id + secret hardcoded as argparse defaults in `main.py`; in every commit that contains the file (since 2022-05-23); repo public | Removed from tree. **Key must be revoked (owner).** History not rewritten. |
| F2 | High | bandit, ruff `S` rules and semgrep `p/secrets` all missed F1 (argparse default) | Documented; secret-pattern test added; secret scan recommended |
| F3 | Medium | `fifth.py` crashes on the header row of `main.py`'s own CSV (default flow broken) | Fixed + regression test |
| F4 | Medium | Bare `%` in argparse help: `--help` crashes on every Python, parser build crashes on 3.14 | Fixed (`%%`) + test on 3.12 and 3.14 |
| F5 | Medium | `comp.py` 1000-row cap -> IndexError | **Not fixed** (contract unknown); strict xfail test pins it |
| F6 | Low | `fifth.py --input == --output` truncated its own input | Fixed + test |
| F7 | Low | Removing `--user/--password` made argparse echo the values ("unrecognized arguments ...") into stderr/cron mail for old wrappers | Fixed: refused without echo + test (found by blue-team) |
| F8 | Low | Redaction replaced the shorter value first (could leak fragments); import failures reported as generic | Fixed (longest first; real error shown) + tests |
| F9 | Low | Huge JSON integer -> uncaught OverflowError in `main.py` | Fixed + test |
| F10 | Low | Malformed ticker mid-loop left partially written CSVs | Fixed: all rows computed before any file is opened |
| F11 | Info | Output follows symlinks, non-atomic multi-file write, unquoted `name` column (CSV/formula injection), best-effort redaction | Accepted, documented in HANDOFF (same as original) |
| F12 | Info | `tr.py` defective duplicate of `comp.py` (aliased `[[0]*7]*1000` rows, string comparisons) | Left, marked legacy |
| F13 | Info | Output newline was platform-dependent (CRLF on Windows); now LF | Documented; `.gitattributes` protects golden fixtures |

## 5. Files

Changed: `main.py`, `fifth.py`, `README.md`, `.gitignore` (append). Created: `margins.py`, `pytest.ini`,
`requirements.txt`, `requirements-dev.txt`, `.gitattributes`, `HANDOFF.md`, `docs/LAST_Report.md`,
`tests/conftest.py`, `tests/test_trader.py`, `tests/fixtures/` (`tickers.json`, `ext_c1/*.csv`, `ext_c10/*.csv`).
Untouched: `comp.py`, `tr.py` (`git diff` empty).

## 6. Command and skill ledger

| Item | Result |
|---|---|
| `/graphify .` | **Partial.** AST pass over code only; semantic extraction of the 51 bootstrap docs skipped on purpose (stub memory files, agent definitions). First graph had 27 nodes because the four scripts had no symbols; graph refreshed with `graphify update .` after the refactor (243 nodes). Health check warned about 15 dangling edges (external imports). |
| `/ponytail:ponytail` | Loaded (namespaced alias registered; `/ponytail` fallback not needed). |
| `/ponytail-review` | Loaded as `ponytail:ponytail-review`; applied by the main session to the original code (5 copy-pasted loops -> one function) and by `sweeper` to the final diff. Not an external tool run. |
| Skill files | `scripts/claude-skill-audit.sh`: all 26 specialist skills + graphify AVAILABLE as files. `scripts/validate-universal-bootstrap.sh`: PASS (checks configuration only). Availability is not proof that each agent invoked its skills. |
| Agents that actually responded (20/20) | triage, product-owner, tech-lead, deep, escalate, prototyper, grower, maintainer, quick, qa-qc, qa-qc-lead (plan review); build (implementation); red-team, red-team-lead, blue-team, blue-team-lead, security-auditor, sweeper, builder (post-implementation); verifier (final). |
| N/A skills | `fastapi-*`, `python-fastapi-development`, `apple-design`, `hardening-docker-containers-for-production` have no FastAPI, UI or Docker artefact to act on; agents were told to say so rather than pretend. |

Conflicts between agents, resolved on evidence: `quick` claimed zero-range inputs raise ZeroDivisionError (false: values are numpy float64, the original warns and writes `nan`; `grower`/`deep`/`qa-qc` were right) and that files were opened before the fetch (false: HEAD fetched first). `tech-lead`/`maintainer`/`prototyper` (credentials optional) beat `product-owner`/`escalate`/`triage` (fail fast) because the SDK constructor is unverified.

## 7. Verification (exact commands, results)

Python 3.12.3 and 3.14.7 venvs under `$SCRATCH` (numpy + pytest); numpy 1.26.4 checked by `builder` in a throwaway venv.

| Check | Result |
|---|---|
| `python -m pytest -q` (3.12.3) | 57 passed, 1 xfailed |
| `python -m pytest -q` (3.14.7) | 57 passed, 1 xfailed |
| numpy 1.26.4 (3.12.3), also with `-W error` | 57 passed, 1 xfailed (re-run by me on the final suite; `builder` had first measured 52 passed on the earlier suite). The 3.12 and 3.14 runs above use numpy 2.5.4. |
| Golden parity | `main.py` CSVs byte-identical to fixtures captured from the original program (12 tickers incl. nan/inf, both clamps, stale `last`, 1e-8 price; coef 1 and 10). `sweeper` also compared HEAD vs new on 3000 random coins at coef 0/1/7/10: CSVs, stdout and exit code identical. |
| Mutation checks | Each new guard was broken in a scratch copy; at least one test failed every time (max/min order, unescaped `%`, header skip, redaction, longest-first, legacy-flag echo, summary count, import message, OverflowError). |
| bandit | 0 findings in product files. 43 Low, all in `tests/test_trader.py` (41 B101 assert, B404, B603). |
| ruff `--select S,B,F,E9` | product files: all checks passed. Whole copy: 41 S101 + 1 S603 + 1 B905, all in tests. |
| semgrep `p/python` + `p/secrets` | 187 rules, 10 files, 0 findings (also 0 on the original: it missed the leak). |
| pip-audit `-r requirements.txt` | No known vulnerabilities (needs network). |
| mypy `--ignore-missing-imports` | Success, no issues in 3 source files. |
| Secret-pattern scan | 0 matches of `[0-9A-Fa-f]{32,}` in every file staged, CSV fixtures included (counts only; values never printed to a file). The same scan on the original `main.py` finds 2. |
| Red-team probes (local, fake values, no network) | No Medium/High. 4 Low + 1 Info (F11 and parts of F8/F9). 300k-row, NaN/inf, NUL-byte and denormal inputs handled. |

**Performance:** not benchmarked by me. The work is O(rows) scalar arithmetic over about a thousand exchange markets;
the only measurement is a `red-team` probe that a 300k-row (~129 MB) input completes. Moving from a 10xN numpy
matrix to numpy scalars per coin is a deliberate fidelity choice (identical nan/inf), not an optimisation.

**Verifier (final pass).** The first run was cut off by an API error before it reported; it was resumed and
completed. Independently re-ran and **passed**: tests on 3.12 and 3.14 (57 passed, 1 xfailed), byte-parity of HEAD
vs the working tree at `--coef 10` and `--coef 0`, the `comp.py` 1000/1001-row behavior (and that the strict xfail
flips to XPASS when the cap is patched), `comp.py`/`tr.py` untouched, the exact commit set (24 files, none of the
bootstrap files), secret-pattern and home-path/e-mail counts of 0, repo visibility PUBLIC. It found four inaccurate
doc statements (commit count, "first commit", the `10**400` behavior, an untested "Python 3.11+" claim), all
corrected above. It did **not** re-run the SAST/pip-audit/mypy counts, the 3000-coin sweep, the mutation checks or
the 300k-row probe: those rest on my own runs and on the named agents' reports. Whether each agent really loaded
its declared skills cannot be proven from the repository.

**Handling slips (disclosed).** Twice a command echoed the key values into a terminal/tool output (my `sed` masking
without the `g` flag, and one `grep` by the verifier). No file, commit or PR text contains them. Three scratch copies of
the original `main.py` were deleted and a re-scan of the scratch directory found none left. Session transcripts
outside the repository may still hold the values, which is one more reason the key must be revoked.

## 8. Role findings

- **Product owner:** scope is right (no UI). The PR must not claim the leak is fixed; "rotate the key" is P0.
- **Tech lead:** pure `margins.py`; builtin `max`/`min` argument order must stay; lazy `coinex` import; creds optional.
- **Red team / red-team lead:** no exploitable Medium+; attack tree: only rotation ends exposure; unresolved dependency name is a typosquat risk (README now says not to `pip install coinex`).
- **Blue team / lead:** hidden legacy flags (fixed), secret scanning + push protection, evidence-first key deletion order, gitleaks pre-commit/CI as follow-up.
- **QA/QC:** golden parity, nan/inf pinning, header regression, strict xfail, count-only secret test.
- **Security auditor:** no new vulnerabilities; `except Exception` at the CLI boundary acceptable.

## 9. Not run / unresolved

- **The leaked key is still live as far as this session can tell.** Rotation is the owner's action (HANDOFF P0). Not validated against CoinEx (deliberately: no use of the credentials).
- gitleaks and trufflehog are not installed; no history-wide secret scan beyond pattern counts and `git log -S`.
- No live CoinEx API call; the `{"ticker": {...}}` response shape is assumed from the original code.
- No Docker build/Compose, frontend build, DAST or web penetration test: nothing of that kind exists in this repo.
- `comp.py` 1000-row cap, `tr.py` defects, symlink/atomic-write/CSV-injection (F5, F11, F12) remain.
- Earlier-requested web-app deliverables (items 1, 8, 9 of the local `docs/REQUEST_COVERAGE_MATRIX.md`, which is not part of this PR) were not executed because the repo is not a web product.
- No `LAST_Report.md` existed before this one, so there was no historical report to clear or reconcile.
