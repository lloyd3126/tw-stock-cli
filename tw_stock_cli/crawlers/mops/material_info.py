"""Fetch MOPS material information announcement lists."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t05st01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t05st01"

COLUMN_MAP = {
    "公司代號": "stock_id",
    "公司名稱": "stock_name",
    "發言日期": "announcement_date",
    "發言時間": "announcement_time",
    "公告日期": "announcement_date",
    "公告時間": "announcement_time",
    "主旨": "subject",
    "主 旨": "subject",
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
        data=material_info_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame()
    return parse_material_info_html(response.text, parameter)


def material_info_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
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
        "co_id": parameter.get("stock_id") or "",
        "year": parameter.get("year"),
        "month": month_value(parameter.get("month")),
        "b_date": day_value(parameter.get("start_day")),
        "e_date": day_value(parameter.get("end_day")),
    }


def parse_material_info_html(html: str, parameter: dict[str, Any]) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    rows: list[dict[str, Any]] = []
    for table in soup.find_all("table"):
        headers = [cell.get_text(" ", strip=True) for cell in table.find_all("th")]
        normalized_headers = [COLUMN_MAP.get(normalize_header(header), "") for header in headers]
        if not {"stock_id", "stock_name", "announcement_date", "announcement_time", "subject"} <= set(
            normalized_headers
        ):
            continue

        source_table = source_table_name(normalized_headers)
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if not cells:
                continue
            record: dict[str, Any] = {
                "query_year": parameter.get("year"),
                "source_table": source_table,
            }
            for index, column in enumerate(normalized_headers):
                if not column or index >= len(cells):
                    continue
                record[column] = clean_cell_text(cells[index].get_text(" ", strip=True))

            detail_attrs = detail_attributes(row)
            record.update(detail_attrs)
            if record.get("stock_id"):
                rows.append(record)

    return pd.DataFrame(rows)


def detail_attributes(row: Any) -> dict[str, str]:
    button = row.find("input", {"type": "button"})
    onclick = button.get("onclick", "") if button else ""
    return {
        "detail_seq_no": onclick_value(onclick, "seq_no"),
        "detail_spoke_date": onclick_value(onclick, "spoke_date"),
        "detail_spoke_time": onclick_value(onclick, "spoke_time"),
        "detail_type": onclick_value(onclick, "TYPEK"),
    }


def onclick_value(onclick: str, name: str) -> str | None:
    match = re.search(rf"{re.escape(name)}\.value='([^']*)'", onclick)
    return match.group(1) if match else None


def source_table_name(columns: list[str]) -> str:
    return "material_info" if "announcement_date" in columns else "material_info"


def normalize_header(header: str) -> str:
    return re.sub(r"\s+", "", header)


def clean_cell_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def month_value(month: Any) -> str:
    if month in (None, ""):
        return ""
    return f"{int(month):02d}"


def day_value(day: Any) -> str:
    if day in (None, ""):
        return ""
    return f"{int(day):02d}"
