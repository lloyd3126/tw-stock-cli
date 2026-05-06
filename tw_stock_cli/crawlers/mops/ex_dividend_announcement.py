"""Fetch MOPS ex-rights and ex-dividend announcement tables."""

from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t108sb27"
REFERER = "https://mopsov.twse.com.tw/mops/web/t108sb27"

NORMALIZED_COLUMN_MAP = {
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "股利所屬期間": "dividend_period",
    "權利分派基準日": "record_date",
    "股票股利_盈餘轉增資配股(元/股)": "stock_dividend_from_earnings_per_share",
    "股票股利_法定盈餘公積、資本公積轉增資配股(元/股)": (
        "stock_dividend_from_reserve_or_capital_surplus_per_share"
    ),
    "股票股利_除權交易日": "ex_rights_date",
    "現金股利_盈餘分配之股東現金股利(元/股)": (
        "cash_dividend_from_earnings_per_share"
    ),
    "現金股利_法定盈餘公積、資本公積發放之現金(元/股)": (
        "cash_dividend_from_reserve_or_capital_surplus_per_share"
    ),
    "現金股利_特別股配發現金股利(元/股)": (
        "preferred_share_cash_dividend_per_share"
    ),
    "現金股利_除息交易日": "ex_dividend_date",
    "現金股利_現金股利發放日": "cash_dividend_payment_date",
    "現金增資總股數(股)": "cash_capital_increase_shares",
    "現金增資認股比率(%)": "cash_capital_increase_subscription_ratio",
    "現金增資認購價(元/股)": "cash_capital_increase_subscription_price",
    "參加分派總股數": "participating_shares",
    "公告日期": "announcement_date",
    "公告時間": "announcement_time",
    "普通股每股面額": "par_value",
}


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    response = requests.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=REFERER,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=ex_dividend_announcement_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_ex_dividend_announcement_html(response.text, parameter)


def ex_dividend_announcement_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    stock_id = parameter.get("stock_id") or ""
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "",
        "TYPEK": parameter.get("kind", "sii"),
        "co_id_1": stock_id,
        "co_id_2": stock_id,
        "year": parameter.get("year"),
        "month": month_value(parameter.get("month")),
        "b_date": day_value(parameter.get("start_day")),
        "e_date": day_value(parameter.get("end_day")),
        "type": parameter.get("sort_type", "1"),
    }


def parse_ex_dividend_announcement_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    soup = BeautifulSoup(html, "html.parser")
    for table in soup.find_all("table", class_="hasBorder"):
        section = section_label(table)
        try:
            parsed = pd.read_html(io.StringIO(str(table)))[0]
        except (ImportError, ValueError):
            continue
        if parsed.empty or len(parsed.columns) < 5:
            continue
        frames.append(normalize_ex_dividend_table(parsed, section, parameter))

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def normalize_ex_dividend_table(
    table: pd.DataFrame,
    section: str | None,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result.columns = ex_dividend_columns(result.columns)
    result = result.rename(columns=ex_dividend_column_name)
    if "stock_id" in result.columns:
        result["stock_id"] = result["stock_id"].astype(str)
    result.insert(0, "query_year", int(parameter.get("year")))
    result.insert(1, "source_section", section)
    return result


def ex_dividend_columns(columns: pd.Index) -> list[str]:
    names = []
    for column in columns:
        parts = column if isinstance(column, tuple) else (column,)
        cleaned = [
            clean_header_part(str(part))
            for part in parts
            if part is not None and not str(part).startswith("Unnamed")
        ]
        deduped: list[str] = []
        for part in cleaned:
            if part and (not deduped or deduped[-1] != part):
                deduped.append(part)
        names.append("_".join(deduped))
    return names


def ex_dividend_column_name(column: str) -> str:
    key = re.sub(r"\s+", "", column)
    return NORMALIZED_COLUMN_MAP.get(key, column)


def section_label(table: Any) -> str | None:
    previous = table.previous_sibling
    while previous is not None:
        text = clean_header_part(getattr(previous, "text", str(previous)))
        if text.startswith("<") and text.endswith(">"):
            return text.strip("<>")
        previous = previous.previous_sibling
    return None


def month_value(month: Any) -> str:
    return "" if month in (None, "", "all") else str(int(month))


def day_value(day: Any) -> str:
    return "" if day in (None, "") else str(int(day))


def clean_header_part(part: str) -> str:
    return re.sub(r"\s+", " ", part.replace("\xa0", " ")).strip()
