"""Fetch MOPS monthly revenue data by company."""

from typing import Any

import pandas as pd
import requests
from loguru import logger
from lxml import etree


HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    "Host": "mops.twse.com.tw",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36",
}


def source_url(kind: str, year: int, month: int, foreign: int) -> str:
    return f"https://mopsov.twse.com.tw/nas/t21/{kind}/t21sc03_{year}_{month}_{foreign}.html"


def parse_month_revenue(html: str, year: int, month: int) -> pd.DataFrame:
    page = etree.HTML(html)
    if page is None:
        return pd.DataFrame()

    stock_ids = [
        cell.text
        for cell in page.xpath("//tr//td[@align='center']")
        if cell.text != "-"
    ]
    cells = page.xpath("//tr//td")
    revenues: list[str] = []
    capture_next_amount = False
    for index, cell in enumerate(cells):
        if capture_next_amount and index + 1 < len(cells):
            amount = cells[index + 1].text or ""
            revenues.append(f"{amount.replace(',', '').replace(' ', '')}000")
        capture_next_amount = cell.text in stock_ids

    return pd.DataFrame(
        {
            "stock_id": stock_ids,
            "revenue": revenues,
            "revenue_year": int(year) + 1911,
            "revenue_month": month,
        }
    )


def crawler(parameter: dict[str, Any]) -> pd.DataFrame:
    logger.info(parameter)
    year = int(parameter.get("year", 111))
    month = int(parameter.get("month", 1))
    kind = str(parameter.get("_type", "sii"))
    foreign = int(parameter.get("foreign", 0))
    response = requests.get(source_url(kind, year, month, foreign), headers=HEADERS)
    response.encoding = "big5"
    if not response.ok or "404" in response.text[:200] or not response.text:
        return pd.DataFrame()
    return parse_month_revenue(response.text, year, month)


if __name__ == "__main__":
    # _type selects listed, OTC, emerging, or public-company pages.
    # foreign selects domestic or foreign-company monthly revenue pages.
    parameter = {"kind": "sii", "year": 111, "month": 1, "_type": "sii", "foreign": 0}
    df = crawler(parameter)
    print(df)
