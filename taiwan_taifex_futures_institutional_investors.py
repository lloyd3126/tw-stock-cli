import typing
import io
import requests

import pandas as pd
from loguru import logger
from lxml import etree


def header():
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Length": "78",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "www.taifex.com.tw",
        "Origin": "https://www.taifex.com.tw",
        "Pragma": "no-cache",
        "Referer": "https://www.taifex.com.tw/cht/3/futContractsDate",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    }


def clean_element(text: str) -> str:
    return (
        text.replace("\r", "")
        .replace("\n", "")
        .replace("\t", "")
        .replace(" ", "")
        .replace(",", "")
    )


def get_future_name(
    resp_text: str,
) -> typing.Tuple[typing.List[str], typing.List[str]]:
    page = etree.HTML(resp_text)
    tem = [
        clean_element(te.text)
        for te in page.xpath('//div[@align="center"]')
        if te.text
    ]
    name = [te for te in tem if "期貨" in te]
    return name


def get_institutional_investors(resp_text: str) -> typing.List[str]:
    page = etree.HTML(resp_text)
    tem = [
        clean_element(te.text)
        for te in page.xpath('//div[@align="center"]')
        if te.text
    ]
    institutional_investors = [te for te in tem if te in ["自營商", "投信", "外資"]]
    return institutional_investors


def get_future_volume(resp_text: str) -> typing.List[str]:
    page = etree.HTML(resp_text)
    volume = [
        clean_element(te.text)
        for te in page.xpath(
            '//tbody//tr[@class="12bk"]//td//div[@align="right"]//font[@color="blue"]'
        )
        if te.text
    ]
    return volume


def get_future_amount(resp_text: str) -> typing.List[str]:
    page = etree.HTML(resp_text)
    amount = [
        clean_element(te.text)
        for te in page.xpath(
            '//tbody//tr[@class="12bk"]//td//div[@align="right"]'
        )
        if te.text
    ]
    amount = [x for x in amount if x]
    return amount


def bind_future(
    name: typing.List[str],
    institutional_investors: typing.List[str],
    volume: typing.List[str],
    amount: typing.List[str],
) -> typing.List[typing.Dict[str, typing.Union[str, int, float]]]:
    future_list = list()
    count = 0
    for i in range(len(name)):
        for j in range(3):
            row = dict(
                futures_id=name[i],
                institutional_investors=institutional_investors[i * 3 + j],
                long_deal_volume=volume[6 * count + 0],
                long_deal_amount=amount[6 * count + 0],
                short_deal_volume=volume[6 * count + 1],
                short_deal_amount=amount[6 * count + 1],
                long_open_interest_balance_volume=volume[6 * count + 3],
                long_open_interest_balance_amount=amount[6 * count + 3],
                short_open_interest_balance_volume=volume[6 * count + 4],
                short_open_interest_balance_amount=amount[6 * count + 4],
            )
            count += 1
            future_list.append(row)
    return future_list


def crawler_future(resp_text: str) -> pd.DataFrame:
    tables = pd.read_html(io.StringIO(resp_text))
    if not tables:
        return pd.DataFrame()
    df = tables[0]
    df.columns = [
        "_".join([str(part).strip() for part in col if not str(part).startswith("Unnamed")]).strip("_")
        if isinstance(col, tuple)
        else str(col).strip()
        for col in df.columns
    ]
    return df


def no_data(resp_text: str) -> bool:
    page = etree.HTML(resp_text)
    temp = page.xpath('//td[@class="13red"]')
    if temp:
        temp = [te.text.replace("\xa0", "") for te in temp]
        if "查無資料" in temp:
            return True
    return False


def crawler(date: str) -> pd.DataFrame:
    form_data = dict(
        queryType="1",
        goDay="",
        doQuery="1",
        dateaddcnt="",
        queryDate=date.replace("-", "/"),
    )

    resp = requests.post(
        url = "https://www.taifex.com.tw/cht/3/futContractsDate",
        headers=header(),
        data=form_data,
    )
    df = pd.DataFrame()
    if no_data(resp.text):
        return df
    else:
        df = crawler_future(resp_text=resp.text)
    return df


if __name__ == "__main__":
    df = crawler(date="2022-05-17")
    print(df)
