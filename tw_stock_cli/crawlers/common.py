"""Shared HTTP and DataFrame helpers for exchange crawler modules."""

import io
from typing import Any, Optional, Sequence

import pandas as pd
import requests


DEFAULT_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}


def compact_date(date: str) -> str:
    """Convert an ISO-like date to YYYYMMDD."""
    return date.replace("-", "")


def roc_date(date: str) -> str:
    """Convert an ISO-like AD date to the ROC date format used by some sources."""
    parts = date.replace("-", "/").split("/")
    parts[0] = str(int(parts[0]) - 1911)
    return "/".join(parts)


def get_json(
    url: str,
    headers: Optional[dict[str, str]] = None,
    timeout: int = 30,
) -> dict[str, Any]:
    """Fetch JSON with exchange-friendly default headers."""
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)
    response = requests.get(url, headers=merged_headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def post(
    url: str,
    data: dict[str, Any],
    headers: Optional[dict[str, str]] = None,
    timeout: int = 30,
) -> requests.Response:
    """POST form data with exchange-friendly default headers."""
    merged_headers = dict(DEFAULT_HEADERS)
    if headers:
        merged_headers.update(headers)
    response = requests.post(url, headers=merged_headers, data=data, timeout=timeout)
    response.raise_for_status()
    return response


def table_dataframe(
    payload: dict[str, Any],
    table_index: int = 0,
    columns: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Convert the common TWSE/TPEx JSON table shape into a DataFrame."""
    if "tables" in payload:
        tables = payload.get("tables") or []
        if not tables:
            return pd.DataFrame()
        table = tables[table_index]
        data = table.get("data", [])
        fields = table.get("fields", [])
    else:
        data = payload.get("data", [])
        fields = payload.get("fields", [])

    if not data:
        return pd.DataFrame()
    return pd.DataFrame(data, columns=columns or fields)


def table_dataframe_by_field(
    payload: dict[str, Any],
    field_name: str,
    columns: Optional[Sequence[str]] = None,
) -> pd.DataFrame:
    """Return the first JSON table whose field list contains the requested field."""
    for table in payload.get("tables", []):
        fields = table.get("fields", [])
        if field_name in fields:
            data = table.get("data", [])
            return pd.DataFrame(data, columns=columns or fields)
    return pd.DataFrame()


def html_tables(html: str) -> list[pd.DataFrame]:
    """Parse HTML tables and normalize source error pages to an empty result."""
    if not html or "PAGE CANNOT BE ACCESSED" in html or "頁面無法執行" in html:
        return []
    return pd.read_html(io.StringIO(html), header=None)
