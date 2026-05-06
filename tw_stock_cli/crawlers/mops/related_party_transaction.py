"""Fetch MOPS related-party transaction monthly disclosure tables."""

from __future__ import annotations

import io
import re
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t141sb02"
REFERER = "https://mopsov.twse.com.tw/mops/web/t141sb02"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "report_month",
    "transaction_type",
    "related_party_name",
    "asset_item",
    "current_month_amount",
    "current_month_ratio",
    "ytd_amount",
    "ytd_ratio",
    "current_month_book_value",
    "current_month_transaction_amount",
    "ytd_transaction_amount",
    "current_month_gain_loss",
    "ytd_gain_loss",
)

SECTION_MAP = {
    "銷貨": {
        "本月銷貨金額": "current_month_amount",
        "占本月合併報表銷貨金額百分比": "current_month_ratio",
        "本年累計銷貨金額": "ytd_amount",
        "占本年合併報表累計銷貨金額百分比": "ytd_ratio",
    },
    "進貨": {
        "本月進貨金額": "current_month_amount",
        "占本月合併報表進貨金額百分比": "current_month_ratio",
        "本年累計進貨金額": "ytd_amount",
        "占本年合併報表累計進貨金額百分比": "ytd_ratio",
    },
    "應收款": {
        "本月應收款增減金額": "current_month_amount",
        "本年累計應收款金額": "ytd_amount",
        "占本年合併報表累計該科目百分比": "ytd_ratio",
    },
    "應付款": {
        "本月應付款增減金額": "current_month_amount",
        "本年累計應付款金額": "ytd_amount",
        "占本年合併報表累計該科目百分比": "ytd_ratio",
    },
    "取得資產": {
        "取得資產項目": "asset_item",
        "本月取得資產金額": "current_month_amount",
        "本年累計取得資產金額": "ytd_amount",
    },
    "處分資產": {
        "處分資產項目": "asset_item",
        "本月處分資產帳面金額": "current_month_book_value",
        "本月處分資產交易金額": "current_month_transaction_amount",
        "本年累計處分資產交易金額": "ytd_transaction_amount",
        "本月處分資產損益": "current_month_gain_loss",
        "本年累計處分資產損益": "ytd_gain_loss",
    },
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
        data=related_party_transaction_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_related_party_transaction_html(response.text, parameter)


def related_party_transaction_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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
        "TYPEK": parameter.get("kind", "sii"),
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def parse_related_party_transaction_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    rows: list[dict[str, Any]] = []
    stock_name = source_company_name(tables)
    section: str | None = None
    for table in tables:
        marker = section_marker(table)
        if marker:
            section = marker
            continue
        if not section or section not in SECTION_MAP:
            continue
        if "關係人名稱" not in [str(column) for column in table.columns]:
            continue
        rows.extend(normalize_section(table, section, stock_name, parameter))

    return pd.DataFrame(rows, columns=OUTPUT_COLUMNS)


def normalize_section(
    table: pd.DataFrame,
    section: str,
    stock_name: str | None,
    parameter: dict[str, Any],
) -> list[dict[str, Any]]:
    column_map = SECTION_MAP[section]
    result = table.rename(columns={column: column_map.get(str(column), str(column)) for column in table.columns})
    rows = []
    for _, source_row in result.iterrows():
        related_party = clean_text(source_row.get("關係人名稱"))
        if not related_party or related_party == "合計":
            continue
        record = {
            "stock_id": str(parameter.get("stock_id")),
            "stock_name": stock_name,
            "market": parameter.get("kind", "sii"),
            "report_year": int(parameter.get("year")),
            "report_month": int(parameter.get("month")),
            "transaction_type": section,
            "related_party_name": related_party,
        }
        for column in OUTPUT_COLUMNS:
            if column in record:
                continue
            value = source_row.get(column)
            record[column] = clean_text(value)
        rows.append(record)
    return rows


def section_marker(table: pd.DataFrame) -> str | None:
    text = " ".join(str(value) for value in table.to_numpy().ravel())
    match = re.search(r"【([^】]+)】", text)
    return match.group(1) if match else None


def source_company_name(tables: list[pd.DataFrame]) -> str | None:
    if not tables:
        return None
    values = [str(value) for value in tables[0].to_numpy().ravel()]
    return values[0] if values else None


def clean_text(value: Any) -> Any:
    if value is None or pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return value
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
