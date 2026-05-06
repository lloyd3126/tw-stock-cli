"""Fetch MOPS employee welfare and salary expense statistics."""

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


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t100sb14"
REFERER = "https://mopsov.twse.com.tw/mops/web/t100sb14"

OUTPUT_COLUMNS = (
    "market",
    "report_year",
    "industry",
    "stock_id",
    "stock_name",
    "company_type",
    "employee_benefit_expense_thousand",
    "employee_salary_expense_thousand",
    "employee_count",
    "avg_employee_benefit_expense_thousand",
    "avg_employee_salary_expense_thousand",
    "previous_avg_employee_salary_expense_thousand",
    "avg_employee_salary_change_ratio",
    "eps",
    "industry_avg_employee_benefit_expense_thousand",
    "industry_avg_employee_salary_expense_thousand",
    "industry_avg_eps",
)

SOURCE_DATA_COLUMNS = (
    "industry",
    "stock_id",
    "stock_name",
    "company_type",
    "employee_benefit_expense_thousand",
    "employee_salary_expense_thousand",
    "employee_count",
    "avg_employee_benefit_expense_thousand",
    "avg_employee_salary_expense_thousand",
    "previous_avg_employee_salary_expense_thousand",
    "avg_employee_salary_change_ratio",
    "eps",
    "industry_avg_employee_benefit_expense_thousand",
    "industry_avg_employee_salary_expense_thousand",
    "industry_avg_eps",
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
        data=employee_salary_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_employee_benefit_expense_html(response.text, parameter)


def employee_salary_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "1",
        "firstin": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "RYEAR": parameter.get("year"),
        "code": parameter.get("industry_code", ""),
    }


def parse_employee_benefit_expense_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html), header=[0, 1])
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    data_tables = [table for table in tables if len(table.columns) >= 15]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return normalize_employee_table(data_tables[0], parameter)


def normalize_employee_table(table: pd.DataFrame, parameter: dict[str, Any]) -> pd.DataFrame:
    rows: list[list[Any]] = []
    for _, row in table.iterrows():
        values = row.tolist()
        if is_stock_id(values[1] if len(values) > 1 else None):
            rows.append(values[: len(SOURCE_DATA_COLUMNS)])
        elif len(values) >= 27 and is_stock_id(values[9]):
            rows.append(
                [
                    values[8],
                    values[9],
                    values[10],
                    values[15],
                    values[16],
                    values[17],
                    values[18],
                    values[19],
                    values[20],
                    values[21],
                    values[22],
                    values[23],
                    values[24],
                    values[25],
                    values[26],
                ]
            )

    result = pd.DataFrame(rows, columns=SOURCE_DATA_COLUMNS)
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "market", parameter.get("kind", "sii"))
    for column in result.columns:
        if column in {"market", "industry", "stock_id", "stock_name", "company_type"}:
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
