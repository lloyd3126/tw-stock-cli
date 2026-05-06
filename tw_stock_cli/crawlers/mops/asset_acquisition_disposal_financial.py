"""Fetch MOPS asset acquisition/disposal financial information tables."""

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
from tw_stock_cli.crawlers.mops.common import company_name_from_html
from tw_stock_cli.crawlers.mops.common import has_no_data


QUERY_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01_q3"
DETAIL_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t12sc01_q3"
ACT = "3"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "report_month",
    "financial_assets_total",
    "total_assets_ratio",
    "equity_ratio",
    "working_capital",
    "pledged_securities_market_value",
    "detail_text",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    query_response = requests.post(
        QUERY_URL,
        headers=mops_headers(REFERER),
        data=asset_acquisition_disposal_financial_query_form_data(parameter),
    )
    if has_no_data(query_response.text):
        return pd.DataFrame()

    query_form = auto_form_data(query_response.text)
    listing_html = query_response.text
    if query_form:
        listing_response = requests.post(
            DETAIL_URL,
            headers=mops_headers(REFERER),
            data=query_form,
        )
        if has_no_data(listing_response.text):
            return pd.DataFrame()
        listing_html = listing_response.text

    detail_form = listing_detail_form_data(listing_html, parameter)
    detail_html = listing_html
    if detail_form:
        detail_response = requests.post(
            DETAIL_URL,
            headers=mops_headers(REFERER),
            data=detail_form,
        )
        if has_no_data(detail_response.text):
            return pd.DataFrame()
        detail_html = detail_response.text

    record = parse_asset_acquisition_disposal_financial_detail_html(
        detail_html,
        parameter,
    )
    return pd.DataFrame([record], columns=OUTPUT_COLUMNS) if record else pd.DataFrame()


def asset_acquisition_disposal_financial_query_form_data(
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
        "TYPEK": parameter.get("kind", "all"),
        "isnew": "false",
        "co_id": parameter.get("stock_id"),
        "year": parameter.get("year"),
        "month": f"{int(parameter.get('month')):02d}",
    }


def parse_asset_acquisition_disposal_financial_detail_html(
    html: str,
    parameter: dict[str, Any],
) -> dict[str, Any]:
    try:
        tables = pd.read_html(io.StringIO(html), header=None)
    except (ImportError, ValueError):
        return {}
    data_tables = [table for table in tables if len(table.columns) >= 2]
    if not data_tables:
        return {}
    fields = key_value_fields(data_tables[-1])
    if not fields:
        return {}
    return {
        "stock_id": str(parameter.get("stock_id")),
        "stock_name": source_company_name(html),
        "market": parameter.get("kind", "all"),
        "report_year": int(parameter.get("year")),
        "report_month": int(parameter.get("month")),
        "financial_assets_total": parse_number(
            field_by_prefix(fields, "截至", "金融資產")
        ),
        "total_assets_ratio": parse_number(
            fields.get("Y占最近期財務報告總資產比率(%)")
        ),
        "equity_ratio": parse_number(
            fields.get("Y占最近期財務報告歸屬於母公司業主之權益比率(%)")
        ),
        "working_capital": parse_number(
            fields.get("最近期財務報告營運資金數額(仟元)")
        ),
        "pledged_securities_market_value": parse_number(
            field_by_prefix(fields, "截至", "有價證券辦理質權設定")
        ),
        "detail_text": " | ".join(
            f"{key}: {value}" for key, value in fields.items() if value
        ),
    }


def auto_form_data(html: str) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", {"name": "autoForm"})
    if form is None:
        return None
    data = hidden_inputs(form)
    data.pop("run", None)
    return data


def listing_detail_form_data(
    html: str,
    parameter: dict[str, Any],
) -> dict[str, Any] | None:
    soup = BeautifulSoup(html, "html.parser")
    form = soup.find("form", {"name": "f1"})
    if form is None:
        return None
    data = hidden_inputs(form)
    data["encodeURIComponent"] = "1"
    data["step"] = data.get("step") or "3"
    data["TYPEK"] = data.get("TYPEK") or parameter.get("kind", "all")
    data["year2"] = data.get("year2") or parameter.get("year")
    data["month2"] = data.get("month2") or f"{int(parameter.get('month')):02d}"
    data["act"] = data.get("act") or ACT
    data["co_id2"] = data.get("co_id2") or parameter.get("stock_id")
    data["firstin"] = "true"
    return data


def hidden_inputs(node: Any) -> dict[str, str]:
    data: dict[str, str] = {}
    for input_tag in node.find_all("input"):
        name = input_tag.get("name")
        if name:
            data[name] = input_tag.get("value", "")
    return data


def key_value_fields(table: pd.DataFrame) -> dict[str, str]:
    fields: dict[str, str] = {}
    for _, source_row in table.iterrows():
        key = clean_text(source_row.iloc[0])
        value = clean_text(source_row.iloc[1])
        if key:
            fields[key] = value or ""
    return fields


def field_by_prefix(
    fields: dict[str, str],
    prefix: str,
    contains: str,
) -> str | None:
    for key, value in fields.items():
        if key.startswith(prefix) and contains in key:
            return value
    return None


def source_company_name(html: str) -> str | None:
    name = company_name_from_html(html)
    if name:
        return name
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    match = re.search(r"本資料由\s*\([^)]*\)\s*([^\s　]+)\s*公司提供", text)
    return match.group(1) if match else None


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def parse_number(value: Any) -> float | None:
    text = clean_text(value)
    if not text:
        return None
    text = text.replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def mops_headers(referer: str) -> dict[str, str]:
    return request_headers(
        accept=HTML_ACCEPT,
        referer=referer,
        origin=STATEMENT_ORIGIN,
        content_type="application/x-www-form-urlencoded",
    )
