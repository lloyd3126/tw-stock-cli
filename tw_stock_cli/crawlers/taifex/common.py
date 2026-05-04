"""Shared helpers for TAIFEX crawler modules."""

import io
import ssl
from typing import Any

import pandas as pd
import requests
from loguru import logger


BASE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "www.taifex.com.tw",
    "Origin": "https://www.taifex.com.tw",
    "Pragma": "no-cache",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36",
}

FCM_HEADERS = {
    **BASE_HEADERS,
    "Content-Type": "application/octet-stream;charset=UTF-8",
    "Referer": "https://www.taifex.com.tw/cht/7/dailyFCM?menuid1=03",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
}


def market_download_headers(referer: str) -> dict[str, str]:
    """Build headers for daily futures/options download endpoints."""
    return {
        **BASE_HEADERS,
        "Content-Length": "101",
        "Content-Type": "application/x-www-form-urlencoded",
        "Referer": referer,
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
    }


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
