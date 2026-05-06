"""Fetch MOPS single-company dividend distribution tables."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import html_tables
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t05st09_2"
REFERER = "https://mopsov.twse.com.tw/mops/web/t05st09_2"

NORMALIZED_COLUMN_MAP = {
    "決議（擬議）進度": "resolution_status",
    "股利所屬年(季)度": "dividend_year",
    "股利所屬期間": "dividend_period",
    "期別": "period_type",
    "董事會決議(擬議)股利分派日": "board_resolution_date",
    "股東會日期": "shareholders_meeting_date",
    "期初未分配盈餘/待彌補虧損(元)": "beginning_retained_earnings_or_deficit",
    "本期淨利(淨損)(元)": "net_income",
    "可分配盈餘(元)": "distributable_earnings",
    "分配後期末未分配盈餘(元)": "ending_retained_earnings",
    "股東配發內容_盈餘分配之現金股利(元/股)": "cash_dividend_per_share",
    "股東配發內容_法定盈餘公積發放之現金(元/股)": "legal_reserve_cash_per_share",
    "股東配發內容_資本公積發放之現金(元/股)": "capital_surplus_cash_per_share",
    "股東配發內容_股東配發之現金(股利)總金額(元)": "total_cash_dividend",
    "股東配發內容_盈餘轉增資配股(元/股)": "stock_dividend_from_earnings_per_share",
    "股東配發內容_法定盈餘公積轉增資配股(元/股)": "stock_dividend_from_legal_reserve_per_share",
    "股東配發內容_資本公積轉增資配股(元/股)": "stock_dividend_from_capital_surplus_per_share",
    "股東配發內容_股東配股總股數(股)": "total_stock_dividend_shares",
    "股利分派之公司章程": "policy_text",
    "備註": "notes",
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
        data=dividend_distribution_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    tables = [table for table in html_tables(response.text) if len(table.columns) >= 5]
    if not tables:
        return pd.DataFrame()
    return normalize_dividend_distribution_table(
        tables[-1],
        response.text,
        parameter,
    )


def dividend_distribution_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    year = parameter.get("year")
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "off": "1",
        "keyword4": "",
        "code1": "",
        "TYPEK2": "",
        "checkbtn": "",
        "queryName": "co_id",
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "all"),
        "isnew": "false",
        "co_id": parameter.get("stock_id"),
        "date1": year,
        "date2": year,
        "qryType": "1",
    }


def normalize_dividend_distribution_table(
    table: pd.DataFrame,
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result.columns = dividend_columns(result.columns)
    result = result.rename(columns=dividend_column_name)

    result.insert(0, "query_year", int(parameter.get("year")))
    result.insert(0, "stock_name", company_name_from_html(html))
    result.insert(0, "stock_id", str(parameter.get("stock_id")))

    return result


def dividend_columns(columns: pd.Index) -> list[str]:
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


def dividend_column_name(column: str) -> str:
    key = re.sub(r"\s+", "", column)
    return NORMALIZED_COLUMN_MAP.get(key, column)


def clean_header_part(part: str) -> str:
    return re.sub(r"\s+", " ", part).strip()
