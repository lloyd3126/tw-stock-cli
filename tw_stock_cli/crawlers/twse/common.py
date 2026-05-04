"""Shared helpers for TWSE crawler modules."""

import requests

from tw_stock_cli.crawlers.common import compact_date


JSON_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "www.twse.com.tw",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

NO_DATA_STATUSES = {
    "很抱歉，沒有符合條件的資料!",
    "查詢日期小於94年9月2日，請重新查詢!",
    "查詢日期小於101年05月02日，請重新查詢!",
}


def headers(referer: str) -> dict[str, str]:
    """Build TWSE JSON request headers for a source page."""
    return {**JSON_HEADERS, "Referer": referer}


def get_json(url: str, date: str, referer: str) -> dict:
    """Fetch a TWSE JSON endpoint whose date parameter uses YYYYMMDD."""
    response = requests.get(
        url.format(date=compact_date(date)), headers=headers(referer)
    )
    response.encoding = "utf-8"
    return response.json()


def is_no_data(payload: dict) -> bool:
    """Return whether a TWSE payload represents an empty historical result."""
    return payload.get("stat") in NO_DATA_STATUSES
