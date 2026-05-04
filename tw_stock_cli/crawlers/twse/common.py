"""Shared helpers for TWSE crawler modules."""

import requests

from tw_stock_cli.crawlers.common import compact_date
from tw_stock_cli.crawlers.common import JSON_ACCEPT
from tw_stock_cli.crawlers.common import request_headers


NO_DATA_STATUSES = {
    "很抱歉，沒有符合條件的資料!",
    "查詢日期小於94年9月2日，請重新查詢!",
    "查詢日期小於101年05月02日，請重新查詢!",
}


def headers(referer: str) -> dict[str, str]:
    """Build TWSE JSON request headers for a source page."""
    return request_headers(accept=JSON_ACCEPT, referer=referer, ajax=True)


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
