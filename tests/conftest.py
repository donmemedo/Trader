import json
import sys
import types
from pathlib import Path

import pytest

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def coinex_stub(monkeypatch):
    """Fake `coinex.coinex.CoinEx` (the real library is never imported). Tests tweak .tickers / .error."""
    monkeypatch.delenv("COINEX_ACCESS_ID", raising=False)
    monkeypatch.delenv("COINEX_SECRET_KEY", raising=False)

    class Stub:
        calls = []
        error = None
        # the {"ticker": {...}} response shape is ASSUMED from main.py's `b['ticker']`
        tickers = json.loads((FIX / "tickers.json").read_text())

        def __init__(self, access_id, secret):
            Stub.calls.append((access_id, secret))

        def market_ticker_all(self):
            if Stub.error:
                raise Stub.error
            return Stub.tickers

    pkg, mod = types.ModuleType("coinex"), types.ModuleType("coinex.coinex")
    mod.CoinEx, pkg.coinex = Stub, mod
    monkeypatch.setitem(sys.modules, "coinex", pkg)
    monkeypatch.setitem(sys.modules, "coinex.coinex", mod)
    return Stub


@pytest.fixture
def work(tmp_path, monkeypatch):
    """Empty cwd, so Custom_Margin.csv lands in tmp_path too."""
    monkeypatch.chdir(tmp_path)
    return tmp_path
