"""Fetch MOPS related-party transaction audit/review difference explanations."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t141sb03"
REFERER = "https://mopsov.twse.com.tw/mops/web/t141sb03"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "quarter",
    "transaction_type",
    "reported_amount",
    "audited_reviewed_amount",
    "difference_amount",
    "difference_ratio",
    "difference_reason",
    "countermeasure",
    "remark",
)

COLUMN_MAP = {
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "項目": "transaction_type",
    "交易類型": "transaction_type",
    "關係人交易項目": "transaction_type",
    "申報數": "reported_amount",
    "自結數": "reported_amount",
    "查核數": "audited_reviewed_amount",
    "核閱數": "audited_reviewed_amount",
    "會計師查核數": "audited_reviewed_amount",
    "會計師核閱數": "audited_reviewed_amount",
    "會計師查核(核閱)數": "audited_reviewed_amount",
    "差異數": "difference_amount",
    "差異金額": "difference_amount",
    "差異比率": "difference_ratio",
    "差異比例": "difference_ratio",
    "差異原因": "difference_reason",
    "原因": "difference_reason",
    "說明": "difference_reason",
    "因應措施": "countermeasure",
    "備註": "remark",
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
        data=related_party_transaction_difference_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_related_party_transaction_difference_html(response.text, parameter)


def related_party_transaction_difference_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
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
        "season": str(int(parameter.get("quar", parameter.get("quarter", 1)))),
    }


def parse_related_party_transaction_difference_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [table for table in tables if len(table.columns) >= 3]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    table = max(data_tables, key=len)
    result = normalize_table(table)
    if result.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    if "stock_id" not in result.columns:
        result["stock_id"] = str(parameter.get("stock_id"))
    if "market" not in result.columns:
        result["market"] = parameter.get("kind", "sii")
    if "report_year" not in result.columns:
        result["report_year"] = int(parameter.get("year"))
    if "quarter" not in result.columns:
        result["quarter"] = int(parameter.get("quar", parameter.get("quarter", 1)))

    for column in OUTPUT_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA
    for column in {
        "reported_amount",
        "audited_reviewed_amount",
        "difference_amount",
        "difference_ratio",
    }:
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    return result[list(OUTPUT_COLUMNS)]


def normalize_table(table: pd.DataFrame) -> pd.DataFrame:
    result = table.copy()
    result.columns = [COLUMN_MAP.get(normalize_key(column), "") for column in result.columns]
    result = result.loc[:, [bool(column) for column in result.columns]]
    if result.empty:
        return result
    for column in result.columns:
        if column in {"reported_amount", "audited_reviewed_amount", "difference_amount", "difference_ratio"}:
            continue
        result[column] = result[column].map(clean_text)
    if "transaction_type" in result.columns:
        result = result[result["transaction_type"].notna()]
        result = result[~result["transaction_type"].isin({"合計", "總計"})]
    return result.reset_index(drop=True)


def normalize_key(column: Any) -> str:
    parts = column if isinstance(column, tuple) else (column,)
    text = "".join(
        str(part)
        for part in parts
        if part is not None and not str(part).startswith("Unnamed")
    )
    text = re.sub(r"\s+", "", text.replace("\xa0", ""))
    text = text.replace("（", "(").replace("）", ")")
    return text


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def clean_number_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    return re.sub(r"[,%]", "", text)
