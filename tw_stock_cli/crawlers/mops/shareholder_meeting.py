"""Fetch MOPS shareholder meeting date and location tables."""

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
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t108sb31"
REFERER = "https://mopsov.twse.com.tw/mops/web/t108sb31_q1"

NORMALIZED_COLUMN_MAP = {
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "公司地址": "company_address",
    "股東常(臨時)會日期": "meeting_type",
    "股東常(臨時)會日期.1": "meeting_date",
    "停止過戶起訖日期": "book_closure_start",
    "停止過戶起訖日期.1": "book_closure_end",
    "召開方式": "meeting_method",
    "開會地點": "location",
    "視訊會議使用平台": "video_conference_platform",
    "是否改選董監": "director_supervisor_election",
    "聯絡電話": "contact_phone",
    "股務單位": "stock_agent",
    "股務單位電話": "stock_agent_phone",
    "行使期間": "e_voting_period",
    "電子投票平台": "e_voting_platform",
    "投票網址": "e_voting_url",
    "異議股東得行使股份收買請求權": "appraisal_rights",
    "公告日期": "announcement_date",
    "公告時間": "announcement_time",
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
        data=shareholder_meeting_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    tables = [table for table in html_tables(response.text) if len(table.columns) >= 10]
    if not tables:
        return pd.DataFrame()
    return normalize_shareholder_meeting_table(tables[-1], parameter)


def shareholder_meeting_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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
        "inpuType": "co_id",
        "TYPEK": parameter.get("kind", "sii"),
        "co_id1": stock_id,
        "co_id2": stock_id,
        "YEAR": parameter.get("year"),
        "MONTH": month_value(parameter.get("month")),
        "SDAY": day_value(parameter.get("start_day")),
        "EDAY": day_value(parameter.get("end_day")),
        "SK": parameter.get("sort_type", "1"),
    }


def normalize_shareholder_meeting_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.copy()
    result = result.rename(columns=shareholder_meeting_column_name)
    result = result[
        ~(
            result.get("book_closure_start", pd.Series(dtype=object)).astype(str)
            == "起"
        )
    ].copy()
    if "stock_id" in result.columns:
        result["stock_id"] = result["stock_id"].astype(str)
    result.insert(0, "query_year", int(parameter.get("year")))
    return result.reset_index(drop=True)


def shareholder_meeting_column_name(column: str) -> str:
    key = re.sub(r"\s+", "", str(column))
    return NORMALIZED_COLUMN_MAP.get(key, str(column))


def month_value(month: Any) -> str:
    return "all" if month in (None, "", "all") else str(int(month))


def day_value(day: Any) -> str:
    return "" if day in (None, "") else str(int(day))
