"""Shared helpers for MOPS crawler modules."""

from typing import Any

import pandas as pd
import requests

from tw_stock_cli.crawlers.common import html_tables


STATEMENT_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "mopsov.twse.com.tw",
    "Origin": "https://mopsov.twse.com.tw",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
}

NO_DATA_MARKERS = (
    "之公司不存在！",
    "查無所需資料",
    "公司不繼續公開發行！",
    "資料庫中查無需求資料",
    "查詢無資料!",
)


def statement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    """Build the form payload used by MOPS quarterly statement endpoints."""
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "isQuery": "Y",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year", 111),
        "season": f"0{parameter.get('quar', 1)}",
    }


def has_no_data(response_text: str) -> bool:
    """Return whether a MOPS HTML response represents an empty result."""
    return not response_text or any(
        marker in response_text for marker in NO_DATA_MARKERS
    )


def fetch_statement_tables(
    url: str,
    referer: str,
    parameter: dict[str, Any],
) -> list[pd.DataFrame]:
    """Fetch and parse a MOPS quarterly statement into tables."""
    headers = {**STATEMENT_HEADERS, "Referer": referer}
    response = requests.post(url, headers=headers, data=statement_form_data(parameter))
    if has_no_data(response.text):
        return []
    return html_tables(response.text)
