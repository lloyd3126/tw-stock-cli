"""Shared helpers for MOPS insider transfer declaration tables."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t56sb21"

DECLARATION_COLUMNS = (
    "change_status",
    "declaration_date",
    "stock_id",
    "stock_name",
    "declarer_role",
    "declarer_name",
    "transfer_method",
    "planned_transfer_shares",
    "max_daily_intraday_transfer_shares",
    "transferee",
    "current_own_shares",
    "current_trust_shares",
    "planned_transfer_own_shares",
    "planned_transfer_trust_shares",
    "post_transfer_own_shares",
    "post_transfer_trust_shares",
    "effective_transfer_period",
    "untransferred_report_filed",
)
UNTRANSFERRED_COLUMNS = (
    "declaration_date",
    "stock_id",
    "stock_name",
    "declarer_role",
    "declarer_name",
    "untransferred_own_shares",
    "untransferred_trust_shares",
    "current_own_shares",
    "current_trust_shares",
    "original_planned_transfer_own_shares",
    "original_planned_transfer_trust_shares",
    "untransferred_reason",
)

DECLARATION_NUMERIC_COLUMNS = (
    "planned_transfer_shares",
    "max_daily_intraday_transfer_shares",
    "current_own_shares",
    "current_trust_shares",
    "planned_transfer_own_shares",
    "planned_transfer_trust_shares",
    "post_transfer_own_shares",
    "post_transfer_trust_shares",
)
UNTRANSFERRED_NUMERIC_COLUMNS = (
    "untransferred_own_shares",
    "untransferred_trust_shares",
    "current_own_shares",
    "current_trust_shares",
    "original_planned_transfer_own_shares",
    "original_planned_transfer_trust_shares",
)


def fetch_transfer_table(
    parameter: dict[str, Any],
    *,
    sstep: int,
    report_type: str,
    referer: str,
) -> pd.DataFrame:
    logger.info(parameter)
    response = requests.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=referer,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=transfer_form_data(parameter, sstep=sstep),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_transfer_html(response.text, parameter, report_type=report_type)


def transfer_form_data(parameter: dict[str, Any], *, sstep: int) -> dict[str, Any]:
    return {
        "encodeURIComponent": "1",
        "step": "1",
        "firstin": "true",
        "TYPEK": parameter.get("kind", "all"),
        "co_id": parameter.get("stock_id", ""),
        "year": parameter.get("year"),
        "smonth": month_value(parameter.get("start_month")),
        "emonth": month_value(parameter.get("end_month")),
        "isnew": "false" if parameter.get("stock_id") else "",
        "sstep": str(sstep),
    }


def parse_transfer_html(
    html: str,
    parameter: dict[str, Any],
    *,
    report_type: str,
) -> pd.DataFrame:
    try:
        tables = [table for table in pd.read_html(io.StringIO(html)) if not table.empty]
    except (ImportError, ValueError):
        return pd.DataFrame()
    if not tables:
        return pd.DataFrame()

    table = tables[0]
    if len(table.columns) >= len(DECLARATION_COLUMNS):
        return normalize_declaration_table(table, parameter, report_type=report_type)
    if len(table.columns) >= len(UNTRANSFERRED_COLUMNS):
        return normalize_untransferred_table(table, parameter, report_type=report_type)
    return pd.DataFrame()


def normalize_declaration_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
    *,
    report_type: str,
) -> pd.DataFrame:
    result = table.iloc[:, : len(DECLARATION_COLUMNS)].copy()
    result.columns = list(DECLARATION_COLUMNS)
    result = normalize_common_columns(result, parameter, report_type)
    for column in DECLARATION_NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(
            result[column].astype(str).map(clean_number_text),
            errors="coerce",
        ).astype("Int64")
    return result[
        [
            "query_year",
            "start_month",
            "end_month",
            "report_type",
            *DECLARATION_COLUMNS,
        ]
    ]


def normalize_untransferred_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
    *,
    report_type: str,
) -> pd.DataFrame:
    result = table.iloc[:, : len(UNTRANSFERRED_COLUMNS)].copy()
    result.columns = list(UNTRANSFERRED_COLUMNS)
    result = normalize_common_columns(result, parameter, report_type)
    for column in UNTRANSFERRED_NUMERIC_COLUMNS:
        result[column] = pd.to_numeric(
            result[column].astype(str).map(clean_number_text),
            errors="coerce",
        ).astype("Int64")
    return result[
        [
            "query_year",
            "start_month",
            "end_month",
            "report_type",
            *UNTRANSFERRED_COLUMNS,
        ]
    ]


def normalize_common_columns(
    frame: pd.DataFrame,
    parameter: dict[str, Any],
    report_type: str,
) -> pd.DataFrame:
    result = frame.copy()
    result.insert(0, "report_type", report_type)
    result.insert(0, "end_month", int(parameter.get("end_month")))
    result.insert(0, "start_month", int(parameter.get("start_month")))
    result.insert(0, "query_year", int(parameter.get("year")))

    for column in result.columns:
        if column in {
            "query_year",
            "start_month",
            "end_month",
            "report_type",
            *DECLARATION_NUMERIC_COLUMNS,
            *UNTRANSFERRED_NUMERIC_COLUMNS,
        }:
            continue
        result[column] = result[column].map(clean_text)

    if "stock_id" in result.columns:
        result["stock_id"] = result["stock_id"].map(stock_id_text)
    return result


def month_value(month: Any) -> str:
    return f"{int(month):02d}"


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    if text.lower() == "nan":
        return None
    return text or None


def stock_id_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    return str(int(float(text))) if re.fullmatch(r"\d+(?:\.0)?", text) else text


def clean_number_text(value: Any) -> str:
    text = clean_text(value)
    return "" if text is None else re.sub(r"[,\s]", "", text)
