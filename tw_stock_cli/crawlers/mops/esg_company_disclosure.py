"""Fetch MOPS ESG company disclosure inquiry metadata."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd
import requests
from loguru import logger

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.mops.common import STATEMENT_ORIGIN
from tw_stock_cli.crawlers.mops.common import has_no_data


URL = "https://mopsov.twse.com.tw/mops/web/ajax_t214sb01"
REFERER = "https://mopsov.twse.com.tw/mops/web/t214sb01"

OUTPUT_COLUMNS = (
    "stock_id",
    "mops_year",
    "report_year",
    "inquiry_url",
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
        data=esg_company_disclosure_form_data(parameter),
    )
    if has_no_data(response.text):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)
    return parse_esg_company_disclosure_html(response.text, parameter)


def esg_company_disclosure_form_data(parameter: dict[str, Any]) -> dict[str, Any]:
    return {
        "step": "2",
        "TYPEK": parameter.get("kind", "sii"),
        "firstin": "1",
        "co_id": parameter.get("stock_id"),
        "YEAR": parameter.get("year"),
    }


def parse_esg_company_disclosure_html(
    html: str,
    parameter: dict[str, Any],
) -> pd.DataFrame:
    inquiry_url = published_inquiry_url(html)
    if not inquiry_url:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    report_year = report_year_from_url(inquiry_url) or to_ad_year(int(parameter.get("year")))
    return pd.DataFrame(
        [
            {
                "stock_id": str(parameter.get("stock_id")),
                "mops_year": int(parameter.get("year")),
                "report_year": report_year,
                "inquiry_url": inquiry_url,
            }
        ],
        columns=OUTPUT_COLUMNS,
    )


def published_inquiry_url(html: str) -> str | None:
    match = re.search(r"window\.open\('([^']+)'", html)
    if not match:
        return None
    return match.group(1).replace("&amp;", "&")


def report_year_from_url(url: str) -> int | None:
    match = re.search(r"[?&]year=(\d+)", url)
    return int(match.group(1)) if match else None


def to_ad_year(year: int) -> int:
    return year + 1911 if year < 1912 else year
