"""Shared helpers for TPEx crawler modules."""

import requests

from tw_stock_cli.crawlers.common import JSON_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.common import roc_date


def headers(referer: str) -> dict[str, str]:
    """Build TPEx JSON request headers for a source page."""
    return request_headers(accept=JSON_ACCEPT, referer=referer, ajax=True)


def get_json(url: str, date: str, referer: str) -> dict:
    """Fetch a TPEx JSON endpoint whose date parameter uses ROC year format."""
    response = requests.get(url.format(date=roc_date(date)), headers=headers(referer))
    response.encoding = "utf-8"
    return response.json()
