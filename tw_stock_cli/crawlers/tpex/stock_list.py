"""Fetch TPEx OTC security codes and names for a trading date."""

from typing import Any

import pandas as pd
import requests
from loguru import logger
from lxml import etree

from tw_stock_cli.crawlers.common import HTML_ACCEPT
from tw_stock_cli.crawlers.common import request_headers
from tw_stock_cli.crawlers.common import roc_date
from tw_stock_cli.crawlers.common import table_dataframe
from tw_stock_cli.crawlers.tpex.common import headers


CATEGORY_URL = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430.php?l=zh-tw"
QUOTE_URL = "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&d={date}&se={category_id}"


def excluded_categories() -> set[str]:
    return {
        "全部",
        "全部(不含權證、牛熊證、可展延牛熊證)",
        "所有證券(不含權證、牛熊證)",
        "封閉式基金",
        "受益證券",
        "認購售權證",
        "展延型牛熊證",
        "認購權證(不含牛證)",
        "認售權證(不含熊證)",
        "牛證(不含可展延牛證)",
        "熊證(不含可展延熊證)",
        "牛熊證(不含展延型牛熊證)",
        "可展延牛證",
        "可展延熊證",
        "附認股權特別股",
        "附認股權公司債",
        "可轉換公司債",
        "認股權憑證",
        "所有證券",
        "委託及成交資訊(16:05提供)",
    }


def create_industry_category_id() -> list[dict[str, Any]]:
    res = requests.get(
        CATEGORY_URL,
        headers=request_headers(
            accept=HTML_ACCEPT,
            cache_control="no-cache",
            upgrade_insecure=True,
        ),
    )
    res.encoding = "utf-8"
    page = etree.HTML(res.text)
    if page is None:
        return []
    temp = page.xpath("//option")
    excluded = excluded_categories()
    loop_list = [
        dict(_id=te.attrib["value"], industry_category=te.text, _type="tpex")
        for te in temp
        if te.text and te.text.replace(" ", "") not in excluded
    ]
    return loop_list


def crawler(date: str) -> pd.DataFrame:
    original_date = date
    frames = []
    for category in create_industry_category_id():
        logger.info(f"crawler id: {category}")
        response = requests.get(
            QUOTE_URL.format(date=roc_date(date), category_id=category.get("_id")),
            headers=headers(CATEGORY_URL),
        )
        data = table_dataframe(response.json())
        if data.empty:
            continue
        frames.append(data)
    if not frames:
        return pd.DataFrame()
    result = pd.concat(frames, axis=0)
    result["date"] = original_date
    return result


if __name__ == "__main__":
    date = "2022-05-05"
    data = crawler(date)
    print(data)
