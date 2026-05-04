"""Shared helpers for TAIFEX crawler modules."""

import io
import ssl
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.common import strip_column_names

TAIFEX_ORIGIN = "https://www.taifex.com.tw"

FCM_HEADERS = request_headers(
    accept=HTML_ACCEPT,
    referer="https://www.taifex.com.tw/cht/7/dailyFCM?menuid1=03",
    origin=TAIFEX_ORIGIN,
    content_type="application/octet-stream;charset=UTF-8",
    cache_control="no-cache",
    upgrade_insecure=True,
)
DAILY_MARKET_COLUMN_MAP = {
    "交易日期": "trade_date",
    "契約": "contract",
    "到期月份(週別)": "expiry_month_week",
    "履約價": "strike_price",
    "買賣權": "call_put",
    "開盤價": "open",
    "最高價": "high",
    "最低價": "low",
    "收盤價": "close",
    "漲跌價": "change",
    "漲跌%": "change_pct",
    "成交量": "volume",
    "結算價": "settlement_price",
    "未沖銷契約數": "open_interest",
    "最後最佳買價": "best_bid",
    "最後最佳賣價": "best_ask",
    "歷史最高價": "historical_high",
    "歷史最低價": "historical_low",
    "是否因訊息面暫停交易": "halt_note",
    "交易時段": "session",
    "價差對單式委託成交量": "spread_volume",
    "契約到期日": "contract_expiry_date",
}
FUTURES_TICK_COLUMN_MAP = {
    "成交日期": "trade_date",
    "商品代號": "contract",
    "到期月份(週別)": "expiry_month_week",
    "成交時間": "trade_time",
    "成交價格": "trade_price",
    "成交數量(B+S)": "trade_volume",
    "近月價格": "near_month_price",
    "遠月價格": "far_month_price",
    "開盤集合競價": "opening_auction",
}
OPTIONS_TICK_COLUMN_MAP = {
    "成交日期": "trade_date",
    "商品代號": "contract",
    "履約價格": "strike_price",
    "到期月份(週別)": "expiry_month_week",
    "買賣權別": "call_put",
    "成交時間": "trade_time",
    "成交價格": "trade_price",
    "成交數量(B or S)": "trade_volume",
    "開盤集合競價": "opening_auction",
}


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
    data = read_taifex_csv_response(response, "big5")
    return normalize_daily_market_columns(data)


def fetch_fcm_csv(filename: str) -> pd.DataFrame:
    """Fetch a TAIFEX futures commission merchant CSV file."""
    url = f"https://www.taifex.com.tw/cht/7/getFCMFile?filename={filename}"
    response = requests.get(url=url, headers=FCM_HEADERS)
    data = read_taifex_csv_response(response, "utf-8-sig")
    if data.empty:
        return data
    data = data.astype("str")
    data = data[data["期貨商代號"] != "Date"].reset_index(drop=True)
    return normalize_fcm_columns(data)


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


def normalize_daily_market_columns(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data
    result = strip_column_names(data)
    result = result.loc[:, ~result.columns.str.startswith("Unnamed")]
    return result.rename(columns=DAILY_MARKET_COLUMN_MAP)


def normalize_fcm_columns(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data

    def normalize_column(column: str) -> str:
        if column == "期貨商代號":
            return "fcm_id"
        if column == "名稱":
            return "fcm_name"
        if column == "小計":
            return "subtotal"
        if column == "總計":
            return "total"
        if column == "市佔率":
            return "market_share"
        if column.startswith("總計"):
            return f"total_{column[2:].lower()}"
        return column.lower()

    result = strip_column_names(data)
    result.columns = [normalize_column(column) for column in result.columns]
    return result


def normalize_futures_tick_columns(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data
    return strip_column_names(data).rename(columns=FUTURES_TICK_COLUMN_MAP)


def normalize_options_tick_columns(data: pd.DataFrame) -> pd.DataFrame:
    if data.empty:
        return data
    return strip_column_names(data).rename(columns=OPTIONS_TICK_COLUMN_MAP)
