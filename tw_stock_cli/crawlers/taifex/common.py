"""Shared helpers for TAIFEX crawler modules."""

import io
import ssl
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers

TAIFEX_ORIGIN = "https://www.taifex.com.tw"

FCM_HEADERS = request_headers(
    accept=HTML_ACCEPT,
    referer="https://www.taifex.com.tw/cht/7/dailyFCM?menuid1=03",
    origin=TAIFEX_ORIGIN,
    content_type="application/octet-stream;charset=UTF-8",
    cache_control="no-cache",
    upgrade_insecure=True,
)


def market_download_headers(referer: str) -> dict[str, str]:
    """Build headers for daily futures/options download endpoints."""
    return request_headers(
        accept=HTML_ACCEPT,
        referer=referer,
        origin=TAIFEX_ORIGIN,
        content_type="application/x-www-form-urlencoded",
        cache_control="no-cache",
        upgrade_insecure=True,
    )


def market_form_data(date: str) -> dict[str, str]:
    """Build the daily market download form payload for a single trading date."""
    query_date = date.replace("-", "/")
    return {
        "down_type": "1",
        "commodity_id": "all",
        "queryStartDate": query_date,
        "queryEndDate": query_date,
    }


def read_taifex_csv_response(
    response: requests.Response, encoding: str
) -> pd.DataFrame:
    """Parse a TAIFEX CSV response, returning an empty DataFrame for empty content."""
    if not response.ok or not response.content:
        logger.info("TAIFEX request did not return valid content")
        return pd.DataFrame()
    return pd.read_csv(io.StringIO(response.content.decode(encoding)), index_col=False)


def fetch_daily_market_csv(url: str, referer: str, date: str) -> pd.DataFrame:
    """Fetch daily futures/options market CSV data."""
    response = requests.post(
        url=url,
        headers=market_download_headers(referer),
        data=market_form_data(date),
    )
    return read_taifex_csv_response(response, "big5")


def fetch_fcm_csv(filename: str) -> pd.DataFrame:
    """Fetch a TAIFEX futures commission merchant CSV file."""
    url = f"https://www.taifex.com.tw/cht/7/getFCMFile?filename={filename}"
    response = requests.get(url=url, headers=FCM_HEADERS)
    data = read_taifex_csv_response(response, "utf-8-sig")
    if data.empty:
        return data
    data = data.astype("str")
    return data[data["期貨商代號"] != "Date"].reset_index(drop=True)


def read_zipped_csv(url: str, **read_csv_kwargs: Any) -> pd.DataFrame:
    """Read a TAIFEX zipped CSV URL, tolerating missing files as empty data."""
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
        data = pd.read_csv(url, **read_csv_kwargs)
    except Exception:
        return pd.DataFrame()
    if data.empty:
        return pd.DataFrame()
    return data
