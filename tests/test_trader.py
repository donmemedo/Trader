import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import fifth
import main
from conftest import FIX
from margins import HEADER, csv_lines, margin_row

ROOT = Path(__file__).parent.parent
NAMES = ["half", "third", "quarter", "fifth"]
CSVS = NAMES + ["Custom_Margin"]


def argv(work, coef=10):
    return [a for n in NAMES for a in (f"--{n}", str(work / f"{n}.csv"))] + ["--coef", str(coef)]


def exit_msg(excinfo):
    assert isinstance(excinfo.value.code, str)  # message -> non-zero exit status
    return excinfo.value.code


# 1. golden parity: byte-identical to the ORIGINAL main.py output (fixtures captured from it)
@pytest.mark.parametrize("coef", [1, 10])
def test_golden_parity(coinex_stub, work, coef, capsys):
    main.main(argv(work, coef))
    for n in CSVS:
        assert (work / f"{n}.csv").read_bytes() == (FIX / f"ext_c{coef}" / f"{n}.csv").read_bytes(), n
    out, err = capsys.readouterr()
    assert out == f"Custom Margin is  1/{coef}\n\n"  # unchanged from the original script
    # 12 fixture coins; FLATUSDT, ZEROUSDT and ALLZERO have a non-finite Ratio in every file (counted per file)
    assert err == "wrote 12 coins x 5 files; up to 3 with non-finite ratio per file\n"


# 2. client failure + credentials
def test_no_env_creds_still_runs(coinex_stub, work):
    main.main(argv(work))
    assert coinex_stub.calls == [("", "")]
    assert (work / "half.csv").exists()


def test_env_creds_are_passed(coinex_stub, work, monkeypatch):
    monkeypatch.setenv("COINEX_ACCESS_ID", "fake-id")
    monkeypatch.setenv("COINEX_SECRET_KEY", "fake-secret-value")
    main.main(argv(work))
    assert coinex_stub.calls == [("fake-id", "fake-secret-value")]


def test_fetch_error_hides_secret_and_writes_nothing(coinex_stub, work, monkeypatch):
    monkeypatch.setenv("COINEX_SECRET_KEY", "fake-secret-value")
    coinex_stub.error = RuntimeError("401 rejected key fake-secret-value")
    with pytest.raises(SystemExit) as e:
        main.main(argv(work))
    msg = exit_msg(e)
    assert "COINEX_ACCESS_ID" in msg and "RuntimeError" in msg
    assert "fake-secret-value" not in msg
    assert list(work.iterdir()) == []


def test_missing_client_library(work, monkeypatch):
    monkeypatch.setitem(sys.modules, "coinex", None)
    monkeypatch.setitem(sys.modules, "coinex.coinex", None)
    with pytest.raises(SystemExit) as e:
        main.main(argv(work))
    assert "could not import the `coinex` client library" in exit_msg(e)
    assert list(work.iterdir()) == []


def test_redaction_replaces_the_longest_value_first(coinex_stub, work, monkeypatch):
    monkeypatch.setenv("COINEX_ACCESS_ID", "AB")  # a substring of the secret: replacing it first would leak "z...z"
    monkeypatch.setenv("COINEX_SECRET_KEY", "zABz")
    coinex_stub.error = RuntimeError("bad key zABz")
    with pytest.raises(SystemExit) as e:
        main.main(argv(work))
    assert "bad key ***)" in exit_msg(e)


@pytest.mark.parametrize("flags", [["--user", "FAKEID123"], ["--password", "FAKESECRET456"], ["--password=FAKESECRET456"]])
def test_removed_credential_flags_are_refused_without_echoing_the_value(flags, capsys):
    with pytest.raises(SystemExit) as e:
        main.main(flags)
    err = capsys.readouterr().err
    assert e.value.code == 2 and "was removed" in err and "COINEX_SECRET_KEY" in err
    assert "FAKE" not in err  # an old cron wrapper must not leak its key into stderr/mail


@pytest.mark.parametrize("coin", [
    {"last": "1", "low": "1"},  # missing "high"
    {"last": "abc", "low": "1", "high": "2"},
    {"last": None, "low": "1", "high": "2"},
    {"last": 10**400, "low": "1", "high": "2"},  # a JSON integer too big for float: OverflowError
])
def test_malformed_ticker_writes_nothing(coinex_stub, work, coin):
    coinex_stub.tickers = {"ticker": {"OK": {"last": "1", "low": "1", "high": "2"}, "BAD": coin}}
    with pytest.raises(SystemExit) as e:
        main.main(argv(work))
    assert "malformed ticker data" in exit_msg(e)
    assert list(work.iterdir()) == []


# 3. margin_row against an inline copy of the legacy numpy formula (exact bits via float.hex)
def legacy(last, low, high, d):
    a = np.zeros(10)
    a[1], a[2], a[0] = float(low), float(high), float(last)
    with np.errstate(all="ignore"):
        a[5] = (a[2] - a[1]) / a[1]
        a[6] = (1 - a[5] / d) * a[0]
        a[7] = (1 + a[5] / d) * a[0]
        a[3] = max(a[6], a[1])
        a[4] = min(a[7], a[2])
        a[8] = 100 * (a[4] - a[3]) / a[3]
        a[9] = a[8] / a[5]
    return a


COINS = [("100", "90", "110"), ("5", "5", "5"), ("0.5", "0", "1"), ("0", "0", "0"), ("1e-8", "1e-8", "2e-8")]


@pytest.mark.parametrize("coin", COINS)
@pytest.mark.parametrize("d", [0, 2, 3, 4, 5, 7])
def test_margin_row_matches_legacy(coin, d):
    row = margin_row(*map(float, coin), d)
    assert [float(x).hex() for x in row] == [float(x).hex() for x in legacy(*coin, d)]
    line = csv_lines({"X": dict(zip(("last", "low", "high"), coin))}, d)[0][1]
    assert line == "X," + ",".join("%f" % x for x in row) + "\n"


def test_margin_row_edge_cases():
    assert np.isnan(margin_row(5, 5, 5, 2)[-1])  # zero range: ratio nan, no ZeroDivisionError
    assert np.isinf(margin_row(0.5, 0, 1, 2)[5])  # zero low: profit inf
    assert np.isnan(margin_row(0, 0, 0, 2)[3])  # all-zero: buy nan (pins builtin max order)
    row = margin_row(100, 90, 110, 0)  # divisor 0 clamps to the day's range, no raise
    assert (row[3], row[4]) == (90, 110)


def test_non_negative_coef():
    p = main.build_parser()
    assert p.parse_args(["--coef", "0"]).coef == 0
    for bad in ("-1", "x"):
        with pytest.raises(SystemExit) as e:
            p.parse_args(["--coef", bad])
        assert e.value.code == 2


# 4. empty ticker
def test_empty_ticker_gives_header_only_files(coinex_stub, work):
    coinex_stub.tickers = {"ticker": {}}
    main.main(argv(work))
    for n in CSVS:
        assert (work / f"{n}.csv").read_text() == HEADER + "\n"


# 5. fifth.py
def run_fifth(work, text, *extra):
    (work / "in.csv").write_text(text)
    fifth.main(["--input", str(work / "in.csv"), "--output", str(work / "out.csv"), *extra])
    return (work / "out.csv").read_text()


def test_fifth_skips_header_and_keeps_nonfinite_rows(work):
    out = run_fifth(work, (FIX / "ext_c10" / "half.csv").read_text()).splitlines()
    assert len(out) == 13 and out[0] == HEADER  # header + 12 coins, input header not re-read as data
    assert out[1].startswith("BTCUSDT,100.000000,90.000000,110.000000,")
    assert any(l.startswith("ALLZERO,") and "nan" in l for l in out)


@pytest.mark.parametrize("text", ["", "\n", HEADER + "\n"])
def test_fifth_empty_inputs(work, text):
    assert run_fifth(work, text) == HEADER + "\n"


def test_fifth_malformed_row_writes_nothing(work):
    with pytest.raises(SystemExit) as e:
        run_fifth(work, "BTC,1\n")
    assert "malformed input row" in exit_msg(e)
    assert not (work / "out.csv").exists()


def test_fifth_input_equals_output_is_refused(work):
    f = work / "same.csv"
    f.write_text("BTC,1,1,2\n")
    with pytest.raises(SystemExit) as e:
        fifth.main(["--input", str(f), "--output", str(f)])
    assert "must differ" in exit_msg(e)
    assert f.read_text() == "BTC,1,1,2\n"


def test_fifth_missing_input(work):
    with pytest.raises(SystemExit) as e:
        fifth.main(["--input", str(work / "nope.csv"), "--output", str(work / "out.csv")])
    assert "python main.py" in exit_msg(e)
    assert not (work / "out.csv").exists()


# 6. --help works (the original help strings crashed on unescaped %)
@pytest.mark.parametrize("mod", [main, fifth])
def test_help(mod, capsys):
    with pytest.raises(SystemExit) as e:
        mod.main(["--help"])
    assert e.value.code == 0
    assert "--coef" in capsys.readouterr().out


# 7. no hex-looking 32+ char secret anywhere in the code/docs (assert on the count: never print a match)
def test_no_secret_like_strings():
    files = [ROOT / n for n in ("main.py", "fifth.py", "margins.py", "comp.py", "tr.py", "README.md")]
    files += list(ROOT.glob("requirements*.txt")) + list((ROOT / "tests").glob("*.py"))
    assert len(files) >= 10
    count = sum(len(re.findall(r"[0-9A-Fa-f]{32,}", f.read_text())) for f in files)
    assert count == 0


# 8. known defect in comp.py (not touched here): 1001+ rows overflow its fixed 1000-row array
@pytest.mark.xfail(strict=True, reason="comp.py caps input at 1000 rows (IndexError)")
def test_comp_handles_1001_rows(tmp_path):
    row = ["x"] * 13
    row[12], row[7], row[8], row[2], row[3] = "1", "1.0", "2.0", "0.5", "0.6"
    for n in ("a.csv", "b.csv"):
        (tmp_path / n).write_text((",".join(row) + "\n") * 1001)
    r = subprocess.run([sys.executable, str(ROOT / "comp.py")], cwd=tmp_path, capture_output=True)
    assert r.returncode == 0
