"""Shared helpers for TPEx crawler modules."""

import requests

from tw_stock_cli.crawlers.common import roc_date


JSON_HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "keep-alive",
    "Host": "www.tpex.org.tw",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def headers(referer: str) -> dict[str, str]:
    """Build TPEx JSON request headers for a source page."""
    return {**JSON_HEADERS, "Referer": referer}


def get_json(url: str, date: str, referer: str) -> dict:
    """Fetch a TPEx JSON endpoint whose date parameter uses ROC year format."""
    response = requests.get(url.format(date=roc_date(date)), headers=headers(referer))
    response.encoding = "utf-8"
    return response.json()
