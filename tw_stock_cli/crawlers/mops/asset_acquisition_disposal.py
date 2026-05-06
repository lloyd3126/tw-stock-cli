"""Fetch MOPS monthly asset acquisition or disposal information."""

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


QUERY_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01_q2"
DETAIL_URL = "https://mopsov.twse.com.tw/mops/web/ajax_t12sc01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t12sc01_q2"
ACT = "2"

OUTPUT_COLUMNS = (
    "stock_id",
    "stock_name",
    "market",
    "report_year",
    "report_month",
    "detail_available",
    "detail_text",
)


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    query_response = requests.post(
        QUERY_URL,
        headers=mops_headers(REFERER),
        data=asset_acquisition_disposal_query_form_data(parameter),
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

    listing = parse_asset_acquisition_disposal_html(listing_html, parameter)
    if listing.empty:
        return listing

    records: list[dict[str, Any]] = []
    for row in listing.to_dict("records"):
        detail_form = row.pop("_detail_form", None)
        if not detail_form:
            records.append(row)
            continue
        detail_response = requests.post(
            DETAIL_URL,
            headers=mops_headers(REFERER),
            data=detail_form,
        )
        detail = parse_asset_acquisition_disposal_detail_html(detail_response.text, row)
        records.append({**row, **detail})

    return pd.DataFrame(records, columns=OUTPUT_COLUMNS)


def asset_acquisition_disposal_query_form_data(
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


def parse_asset_acquisition_disposal_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    detail = parse_asset_acquisition_disposal_detail_html(html, {})
    if detail:
        return pd.DataFrame(
            [
                {
                    "stock_id": str(parameter.get("stock_id")),
                    "stock_name": company_name_from_html(html),
                    "market": parameter.get("kind", "all"),
                    "report_year": int(parameter.get("year")),
                    "report_month": int(parameter.get("month")),
                    "detail_available": True,
                    **detail,
                }
            ],
            columns=OUTPUT_COLUMNS,
        )

    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table", class_="hasBorder"):
        headers = [clean_text(cell.get_text(" ", strip=True)) for cell in table.find_all("th")]
        if not {"公司代號", "公司名稱"} <= set(headers):
            continue
        for source_row in table.find_all("tr"):
            cells = source_row.find_all("td")
            if len(cells) < 2:
                continue
            stock_id = clean_text(cells[0].get_text(" ", strip=True))
            if not stock_id or not re.fullmatch(r"\d{4,6}", stock_id):
                continue
            rows.append(
                {
                    "stock_id": stock_id,
                    "stock_name": clean_text(cells[1].get_text(" ", strip=True)),
                    "market": parameter.get("kind", "all"),
                    "report_year": int(parameter.get("year")),
                    "report_month": int(parameter.get("month")),
                    "detail_available": bool(detail_form_data(source_row, parameter)),
                    "detail_text": None,
                    "_detail_form": detail_form_data(source_row, parameter),
                }
            )

    return pd.DataFrame(rows)


def parse_asset_acquisition_disposal_detail_html(
    html: str,
    row: dict[str, Any],
) -> dict[str, Any]:
    if has_no_data(html):
        return {}
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


def detail_form_data(row: Any, parameter: dict[str, Any]) -> dict[str, Any] | None:
    hidden = hidden_inputs(row)
    if hidden.get("step"):
        hidden["co_id2"] = hidden.get("co_id2") or parameter.get("stock_id")
        hidden.pop("run", None)
        return hidden
    button = row.find("input", {"type": "button"})
    if not button:
        return None
    onclick = button.get("onclick", "")
    match = re.search(r"co_id2\.value='([^']+)'", onclick)
    if not match:
        return None
    return {
        "encodeURIComponent": "1",
        "step": "3",
        "TYPEK": parameter.get("kind", "all"),
        "year2": parameter.get("year"),
        "month2": f"{int(parameter.get('month')):02d}",
        "act": ACT,
        "co_id2": match.group(1),
        "firstin": "true",
    }


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


def clean_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    return text or None


def mops_headers(referer: str) -> dict[str, str]:
    return request_headers(
        accept=HTML_ACCEPT,
        referer=referer,
        origin=STATEMENT_ORIGIN,
        content_type="application/x-www-form-urlencoded",
    )
