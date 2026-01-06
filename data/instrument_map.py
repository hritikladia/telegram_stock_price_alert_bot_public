# storage/instrument_map.py

import csv
import os
import time
import urllib.request
from typing import Optional, Tuple, List, Dict

# URL for compact instrument list as per DhanHQ docs  
INSTRUMENT_CSV_URL = "https://images.dhan.co/api-data/api-scrip-master.csv"  # :contentReference[oaicite:1]{index=1}  
CACHE_FILE = os.getenv("INSTRUMENT_CACHE_FILE", "dhan_instruments.csv")
CACHE_TTL_SECONDS = 24 * 60 * 60  # refresh once per 24h

# symbol → list of (security_id, exchange_segment, instrument_segment)  
_symbol_map: Dict[str, List[Tuple[str, str, str]]] = {}

def _download_csv() -> None:
    """Download the latest instrument list CSV from DhanHQ."""
    print("📥 Downloading instrument list from DhanHQ …")
    urllib.request.urlretrieve(INSTRUMENT_CSV_URL, CACHE_FILE)
    print(f"✅ Saved instrument list to {CACHE_FILE}")

def _load_mapping() -> None:
    global _symbol_map

    # download if cache expired
    if not os.path.exists(CACHE_FILE) or time.time() - os.path.getmtime(CACHE_FILE) > CACHE_TTL_SECONDS:
        _download_csv()

    _symbol_map.clear()

    ALLOWED_TYPES = {"ES", "INDEX"}   # <--- only load real equities

    with open(CACHE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:

            instr_type = row.get("SEM_EXCH_INSTRUMENT_TYPE", "").strip().upper()
            if instr_type not in ALLOWED_TYPES:
                continue    # ignore debt, bonds, ETFs, MF, REIT, etc.

            symbol  = row.get("SEM_TRADING_SYMBOL", "").strip().upper()
            sec_id  = row.get("SEM_SMST_SECURITY_ID", "").strip()
            exch    = row.get("SEM_EXM_EXCH_ID", "").strip()
            segment = row.get("SEM_SEGMENT", "").strip()

            if symbol and sec_id and exch and segment:
                _symbol_map.setdefault(symbol, []).append((sec_id, exch, segment))

    print(f"Loaded mapping for {len(_symbol_map)} pure-equity symbols.")

    print("Sample entry:", list(_symbol_map.items())[:5])


def get_security_details(
    symbol: str,
    segment_filter: Optional[str] = None,
    exchange_filter: Optional[str] = None
) -> Optional[Tuple[str, str, str]]:
    """
    Returns (security_id, exchange, segment) for the given symbol.
    Filters by segment and exchange if provided.
    Returns None if:
    - the symbol is not found
    - filters don't match
    - multiple matches exist without enough filters
    """
    if not _symbol_map:
        _load_mapping()

    symbol_uc = symbol.strip().upper()
    candidates = _symbol_map.get(symbol_uc)
    if not candidates:
        return None

    # Apply segment filter first
    if segment_filter:
        candidates = [c for c in candidates if c[2] == segment_filter]
        if not candidates:
            return None

    # Apply exchange filter next
    if exchange_filter:
        candidates = [c for c in candidates if c[1] == exchange_filter]
        if not candidates:
            return None

    # If only one match remains, return it
    if len(candidates) == 1:
        return candidates[0]

    # Still ambiguous
    return None


def search_symbols(
    prefix: str,
    segment_filter: Optional[str] = None,
    exchange_filter: Optional[str] = None,
    limit: int = 5
) -> List[Tuple[str, str, str]]:
    """
    Return up to `limit` matches for a partial symbol prefix.
    Each result is a tuple (symbol, exchange, segment).

    Args:
        prefix: partial symbol name (case-insensitive)
        segment_filter: optional segment filter, e.g. "Equity", "Index", "F&O"
        exchange_filter: optional exchange filter, e.g. "NSE", "BSE"
        limit: maximum number of results to return
    """
    if not _symbol_map:
        _load_mapping()

    prefix_uc = prefix.strip().upper()
    results: List[Tuple[str, str, str]] = []

    for sym, entries in _symbol_map.items():
        if sym.startswith(prefix_uc):
            for (sec_id, exch, seg) in entries:
                if ((segment_filter is None or seg == segment_filter) and
                    (exchange_filter is None or exch == exchange_filter)):
                    results.append((sym, exch, seg))
                    if len(results) >= limit:
                        return results
    return results


if __name__ == "__main__":
    # Quick manual test
    syms = ["RELIANCE", "HDFCBANK", "BANKNIFTY", "500325"]
    for s in syms:
        details = get_security_details(s, 'E', 'NSE')
        print(s, "→", details)
    suggestions = search_symbols("BANKNI","I", "NSE", limit=5)
    print("Suggestions for ‘RELI’: ", suggestions)
