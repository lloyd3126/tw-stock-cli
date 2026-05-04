"""Shared HTTP and DataFrame helpers for exchange crawler modules."""

import io
from typing import Any, Optional, Sequence

import pandas as pd
import requests


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
JSON_ACCEPT = "application/json, text/javascript, */*; q=0.01"
HTML_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
)

DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": DEFAULT_USER_AGENT,
}


def request_headers(
    *,
    accept: str = "*/*",
    referer: Optional[str] = None,
    origin: Optional[str] = None,
    content_type: Optional[str] = None,
    ajax: bool = False,
    cache_control: Optional[str] = None,
    upgrade_insecure: bool = False,
    extra: Optional[dict[str, str]] = None,
) -> dict[str, str]:
    """Build stable browser-like headers while leaving transport headers to requests."""
    headers = {**DEFAULT_HEADERS, "Accept": accept}
    if referer:
        headers["Referer"] = referer
    if origin:
        headers["Origin"] = origin
    if content_type:
        headers["Content-Type"] = content_type
    if ajax:
        headers["X-Requested-With"] = "XMLHttpRequest"
    if cache_control:
        headers["Cache-Control"] = cache_control
        headers["Pragma"] = "no-cache"
    if upgrade_insecure:
        headers["Upgrade-Insecure-Requests"] = "1"
    if extra:
        headers.update(extra)
    return headers


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


def select_and_rename_columns(
    frame: pd.DataFrame,
    source_columns: Sequence[str],
    output_columns: Sequence[str],
) -> pd.DataFrame:
    """Select source columns and rename them to the crawler output contract."""
    if len(source_columns) != len(output_columns):
        raise ValueError("source_columns and output_columns must have the same length")
    result = frame[list(source_columns)].copy()
    result.columns = list(output_columns)
    return result


def flatten_column_names(columns: Sequence[Any]) -> list[str]:
    """Flatten pandas MultiIndex columns into stable string names."""
    names = []
    for column in columns:
        if isinstance(column, tuple):
            parts = [
                str(part).strip()
                for part in column
                if not str(part).startswith("Unnamed")
            ]
            names.append("_".join(parts).strip("_"))
        else:
            names.append(str(column).strip())
    return names


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
