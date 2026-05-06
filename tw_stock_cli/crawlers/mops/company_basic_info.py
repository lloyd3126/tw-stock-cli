"""Fetch MOPS company basic information tables."""

from __future__ import annotations

from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import html_tables
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t51sb01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t51sb01"

COLUMN_MAP = {
    "公司 代號": "stock_id",
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "公司簡稱": "short_name",
    "產業類別": "industry",
    "外國企業 註冊地國": "foreign_registration_country",
    "住址": "address",
    "營利事業 統一編號": "tax_id",
    "董事長": "chairman",
    "總經理": "general_manager",
    "發言人": "spokesperson",
    "發言人職稱": "spokesperson_title",
    "代理發言人": "acting_spokesperson",
    "總機電話": "phone",
    "成立日期": "founded_date",
    "上市日期": "listed_date",
    "上櫃日期": "listed_date",
    "普通股每股面額": "par_value",
    "實收資本額(元)": "paid_in_capital",
    "已發行普通股數或 TDR原發行股數": "issued_common_shares_or_tdr_units",
    "編製財務報告類型": "financial_report_type",
    "公司網址": "website",
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
        data=company_basic_info_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()

    tables = [table for table in html_tables(response.text) if len(table.columns) >= 5]
    if not tables:
        return pd.DataFrame()

    result = normalize_company_basic_info_table(tables[0])
    stock_id = parameter.get("stock_id")
    if stock_id:
        result = result[result["stock_id"].astype(str) == str(stock_id)]
    return result.reset_index(drop=True)


def company_basic_info_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "code": parameter.get("industry_code") or "",
    }


def normalize_company_basic_info_table(table: pd.DataFrame) -> pd.DataFrame:
    result = table.copy()
    result.columns = [str(column).strip() for column in result.columns]
    result = result.rename(columns=COLUMN_MAP)
    return result
