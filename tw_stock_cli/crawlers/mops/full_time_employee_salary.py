"""Fetch MOPS non-manager full-time employee salary statistics."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb15"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb15"

OUTPUT_COLUMNS = (
    "market",
    "report_year",
    "industry",
    "stock_id",
    "stock_name",
    "salary_total_thousand",
    "employee_count_avg",
    "salary_avg_thousand",
    "previous_salary_avg_thousand",
    "salary_avg_change_ratio",
    "salary_median_thousand",
    "previous_salary_median_thousand",
    "salary_median_change_ratio",
    "eps",
    "peer_salary_avg_thousand",
    "peer_avg_eps",
    "salary_avg_below_500k",
    "eps_better_than_peer_salary_below_peer",
    "eps_growth_salary_avg_decline",
    "performance_compensation_reasonableness",
    "improvement_measures",
)

SOURCE_DATA_COLUMNS = (
    "industry",
    "stock_id",
    "stock_name",
    "salary_total_thousand",
    "employee_count_avg",
    "salary_avg_thousand",
    "previous_salary_avg_thousand",
    "salary_avg_change_ratio",
    "salary_median_thousand",
    "previous_salary_median_thousand",
    "salary_median_change_ratio",
    "eps",
    "peer_salary_avg_thousand",
    "peer_avg_eps",
    "salary_avg_below_500k",
    "eps_better_than_peer_salary_below_peer",
    "eps_growth_salary_avg_decline",
    "performance_compensation_reasonableness",
    "improvement_measures",
)


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
        data=full_time_employee_salary_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_full_time_employee_salary_html(response.text, parameter)


def full_time_employee_salary_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "1",
        "firstin": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "RYEAR": parameter.get("year"),
        "code": parameter.get("industry_code", ""),
    }


def parse_full_time_employee_salary_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=[0, 1, 2])
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    data_tables = [
        table for table in tables if len(table.columns) >= len(SOURCE_DATA_COLUMNS)
    ]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = data_tables[0].iloc[:, : len(SOURCE_DATA_COLUMNS)].copy()
    result.columns = SOURCE_DATA_COLUMNS
    result = result[result["stock_id"].map(is_stock_id)].copy()
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "market", parameter.get("kind", "sii"))
    for column in result.columns:
        if column in {
            "market",
            "industry",
            "stock_id",
            "stock_name",
            "salary_avg_below_500k",
            "eps_better_than_peer_salary_below_peer",
            "eps_growth_salary_avg_decline",
            "performance_compensation_reasonableness",
            "improvement_measures",
        }:
            result[column] = result[column].map(clean_text)
            continue
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def is_stock_id(value: Any) -> bool:
    text = clean_text(value)
    return bool(text and re.fullmatch(r"\d{4,6}", text))


def clean_number_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None or text in {"-", "--", "----", "------"}:
        return None
    return re.sub(r"[,%]", "", text)


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None
