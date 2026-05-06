"""Fetch MOPS director and supervisor remuneration summary tables."""

from __future__ import annotations

import io
import re
from typing import Any
from urllib.parse import urljoin

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t119sb04"
REFERER = "https://mopsov.twse.com.tw/mops/web/t119sb04"

OUTPUT_COLUMNS = (
    "market",
    "report_year",
    "report_type",
    "role",
    "industry",
    "stock_id",
    "stock_name",
    "current_year_base_remuneration",
    "next_year_base_remuneration",
    "base_remuneration_total",
    "current_year_with_employee_salary",
    "next_year_with_employee_salary",
    "with_employee_salary_total",
    "base_remuneration_profit_ratio",
    "with_employee_salary_profit_ratio",
    "average_base_remuneration",
    "average_with_employee_salary",
    "outside_investment_parent_remuneration",
    "after_tax_profit_loss",
    "eps",
    "roe",
    "paid_in_capital_thousand",
    "reasonableness_explanation",
)

DATA_COLUMNS = (
    "industry",
    "stock_id",
    "stock_name",
    "current_year_base_remuneration",
    "next_year_base_remuneration",
    "base_remuneration_total",
    "current_year_with_employee_salary",
    "next_year_with_employee_salary",
    "with_employee_salary_total",
    "base_remuneration_profit_ratio",
    "with_employee_salary_profit_ratio",
    "average_base_remuneration",
    "average_with_employee_salary",
    "outside_investment_parent_remuneration",
    "after_tax_profit_loss",
    "eps",
    "roe",
    "paid_in_capital_thousand",
    "reasonableness_explanation",
)

REPORT_TYPE_LABELS = {
    "1": "company",
    "2": "consolidated",
}

ROLE_LABELS = {
    "A": "director",
    "B": "supervisor",
}


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    session = requests.Session()
    response = session.post(
        URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            referer=REFERER,
            origin=STATEMENT_ORIGIN,
            content_type="application/x-www-form-urlencoded",
        ),
        data=director_supervisor_remuneration_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    report_url = published_report_url(response.text)
    html = response.text
    if report_url:
        report_response = session.get(
            report_url,
            headers=request_headers(accept=HTML_ACCEPT, referer=REFERER),
        )
        html = report_response.content.decode("big5", errors="replace")

    return parse_director_supervisor_remuneration_html(html, parameter)


def director_supervisor_remuneration_form_data(
    parameter: dict[str, Any],
) -> dict[str, Any]:
    return {
        "step": "1",
        "firstin": "ture",
        "off": "1",
        "TYPEK": parameter.get("kind", "sii"),
        "year": parameter.get("year"),
        "rid": parameter.get("report_type", "1"),
        "wid": parameter.get("role", "A"),
        "sid": parameter.get("sort_by", "2"),
    }


def parse_director_supervisor_remuneration_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    try:
        tables = pd.read_html(io.StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    data_tables = [table for table in tables if len(table.columns) >= len(DATA_COLUMNS)]
    if not data_tables:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = normalize_remuneration_table(data_tables[0], parameter)
    return result


def normalize_remuneration_table(
    table: pd.DataFrame,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    result = table.iloc[:, : len(DATA_COLUMNS)].copy()
    result.columns = DATA_COLUMNS
    result = result[result["stock_id"].map(is_stock_id)].copy()

    result.insert(0, "role", ROLE_LABELS.get(str(parameter.get("role", "A")), "director"))
    result.insert(
        0,
        "report_type",
        REPORT_TYPE_LABELS.get(str(parameter.get("report_type", "1")), "company"),
    )
    result.insert(0, "report_year", int(parameter.get("year")))
    result.insert(0, "market", parameter.get("kind", "sii"))

    for column in result.columns:
        if column in {
            "market",
            "report_type",
            "role",
            "industry",
            "stock_id",
            "stock_name",
            "reasonableness_explanation",
        }:
            result[column] = result[column].map(clean_text)
            continue
        result[column] = pd.to_numeric(
            result[column].map(clean_number_text),
            errors="coerce",
        )

    result["stock_id"] = result["stock_id"].astype(str)
    return result[list(OUTPUT_COLUMNS)].reset_index(drop=True)


def published_report_url(html: str) -> str | None:
    match = re.search(r"window\.open\('([^']+)'", html)
    if not match:
        return None
    return urljoin("https://mopsov.twse.com.tw", match.group(1))


def is_stock_id(value: Any) -> bool:
    text = clean_text(value)
    return bool(text and re.fullmatch(r"\d{4,6}", text))


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def clean_number_text(value: Any) -> str | None:
    text = clean_text(value)
    if text is None:
        return None
    if text in {"-", "--", "----", "------"}:
        return None
    return re.sub(r"[,%]", "", text)
