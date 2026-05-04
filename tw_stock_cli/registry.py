"""Dataset catalog and dispatch logic for the tw-stock CLI."""

from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Literal

import pandas as pd


DatasetKind = Literal["date", "none", "mops-month", "mops-quarter"]


@dataclass(frozen=True)
class Dataset:
    id: str
    title: str
    group: str
    description: str
    module: str
    kind: DatasetKind
    returns: tuple[str, ...]
    source_urls: tuple[str, ...]
    notes: str = ""

    def fetch(self, params: dict[str, Any]) -> pd.DataFrame | list[pd.DataFrame]:
        module = import_module(self.module)
        if self.kind == "date":
            date = require(params, "date")
            # Legacy price crawlers still accept their date inside a parameter dict.
            if self.id in {"twse.stock-price", "tpex.stock-price"}:
                return module.crawler({"crawler_date": date})
            return module.crawler(date)

        if self.kind == "none":
            return module.crawler()

        if self.kind == "mops-month":
            # MOPS endpoints use ROC years even when the CLI accepts AD years.
            year = normalize_roc_year(int(require(params, "year")))
            month = int(require(params, "month"))
            market = params.get("market", "sii")
            foreign = int(params.get("foreign", 0))
            return module.crawler(
                {
                    "kind": market,
                    "year": year,
                    "month": month,
                    "_type": market,
                    "foreign": foreign,
                }
            )

        if self.kind == "mops-quarter":
            # MOPS quarterly statement endpoints use ROC years.
            year = normalize_roc_year(int(require(params, "year")))
            quarter = int(require(params, "quarter"))
            market = params.get("market", "sii")
            return module.crawler({"kind": market, "year": year, "quar": quarter})

        raise ValueError(f"Unsupported dataset kind: {self.kind}")


def require(params: dict[str, Any], key: str) -> Any:
    value = params.get(key)
    if value in (None, ""):
        raise ValueError(f"Missing required parameter: {key}")
    return value


def normalize_roc_year(year: int) -> int:
    return year - 1911 if year >= 1912 else year


DATASETS: dict[str, Dataset] = {
    "twse.stock-price": Dataset(
        id="twse.stock-price",
        title="上市股票每日收盤價",
        group="twse",
        description="Daily close quotes for TWSE listed securities, including open, high, low, and close.",
        module="tw_stock_cli.crawlers.twse.stock_price",
        kind="date",
        returns=("stock_id", "stock_name", "open", "high", "low", "close", "date"),
        source_urls=("https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",),
    ),
    "twse.stock-list": Dataset(
        id="twse.stock-list",
        title="上市股票清單",
        group="twse",
        description="TWSE listed security codes and names for a trading date.",
        module="tw_stock_cli.crawlers.twse.stock_list",
        kind="date",
        returns=("stock_id", "stock_name", "date"),
        source_urls=("https://www.twse.com.tw/rwd/zh/afterTrading/MI_INDEX",),
    ),
    "twse.stock-per": Dataset(
        id="twse.stock-per",
        title="上市本益比與殖利率",
        group="twse",
        description="TWSE PER, dividend yield, and price-to-book ratio by security.",
        module="tw_stock_cli.crawlers.twse.stock_valuation",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "close",
            "dividend_yield",
            "dividend_year",
            "per",
            "pbr",
            "financial_report_period",
            "date",
        ),
        source_urls=("https://www.twse.com.tw/exchangeReport/BWIBBU_d",),
    ),
    "twse.institutional-trade": Dataset(
        id="twse.institutional-trade",
        title="上市三大法人買賣超",
        group="twse",
        description="TWSE daily institutional investor buy/sell details.",
        module="tw_stock_cli.crawlers.twse.institutional_trade",
        kind="date",
        returns=("stock_id", "stock_name", "institutional_net_buy"),
        source_urls=("https://www.twse.com.tw/fund/T86",),
    ),
    "twse.margin-trade": Dataset(
        id="twse.margin-trade",
        title="上市融資融券餘額",
        group="twse",
        description="TWSE margin purchase and short sale balances.",
        module="tw_stock_cli.crawlers.twse.margin_trade",
        kind="date",
        returns=("stock_id", "stock_name", "margin_purchase_balance", "short_sale_balance"),
        source_urls=("https://www.twse.com.tw/exchangeReport/MI_MARGN",),
    ),
    "twse.foreign-holding": Dataset(
        id="twse.foreign-holding",
        title="上市外資及陸資持股",
        group="twse",
        description="Foreign and mainland China investor holding statistics for TWSE listed securities.",
        module="tw_stock_cli.crawlers.twse.foreign_holding",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "issued_shares",
            "foreign_held_shares",
            "foreign_held_ratio",
        ),
        source_urls=("https://www.twse.com.tw/fund/MI_QFIIS",),
    ),
    "twse.total-return-index": Dataset(
        id="twse.total-return-index",
        title="發行量加權股價報酬指數",
        group="twse",
        description="TWSE total return index values for the month containing the requested date.",
        module="tw_stock_cli.crawlers.twse.total_return_index",
        kind="date",
        returns=("date", "total_return_index"),
        source_urls=("https://www.twse.com.tw/indicesReport/MFI94U",),
    ),
    "tpex.stock-price": Dataset(
        id="tpex.stock-price",
        title="上櫃股票每日收盤價",
        group="tpex",
        description="Daily close quotes for TPEx securities, including open, high, low, and close.",
        module="tw_stock_cli.crawlers.tpex.stock_price",
        kind="date",
        returns=("stock_id", "stock_name", "close", "open", "high", "low", "date"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php",
        ),
    ),
    "tpex.stock-list": Dataset(
        id="tpex.stock-list",
        title="上櫃股票清單",
        group="tpex",
        description="TPEx security list and daily quote columns by industry category.",
        module="tw_stock_cli.crawlers.tpex.stock_list",
        kind="date",
        returns=("stock_id", "stock_name", "industry_category", "date"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php",
        ),
    ),
    "tpex.stock-per": Dataset(
        id="tpex.stock-per",
        title="上櫃本益比與殖利率",
        group="tpex",
        description="TPEx PER, dividend yield, and price-to-book ratio by security.",
        module="tw_stock_cli.crawlers.tpex.stock_valuation",
        kind="date",
        returns=(
            "stock_id",
            "stock_name",
            "per",
            "dividend_per_share",
            "dividend_year",
            "dividend_yield",
            "pbr",
            "date",
        ),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/aftertrading/peratio_analysis/pera_result.php",
        ),
    ),
    "tpex.institutional-trade": Dataset(
        id="tpex.institutional-trade",
        title="上櫃三大法人買賣超",
        group="tpex",
        description="TPEx daily institutional investor buy/sell details.",
        module="tw_stock_cli.crawlers.tpex.institutional_trade",
        kind="date",
        returns=("stock_id", "stock_name", "institutional_net_buy"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/3insti/daily_trade/3itrade_hedge_result.php",
        ),
    ),
    "tpex.margin-trade": Dataset(
        id="tpex.margin-trade",
        title="上櫃融資融券餘額",
        group="tpex",
        description="TPEx margin purchase and short sale balances.",
        module="tw_stock_cli.crawlers.tpex.margin_trade",
        kind="date",
        returns=("stock_id", "stock_name", "margin_purchase_balance", "short_sale_balance"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/margin_trading/margin_balance/margin_bal_result.php",
        ),
    ),
    "tpex.foreign-holding": Dataset(
        id="tpex.foreign-holding",
        title="上櫃外資持股比例",
        group="tpex",
        description="TPEx foreign investor holding ratio ranking.",
        module="tw_stock_cli.crawlers.tpex.foreign_holding",
        kind="date",
        returns=(
            "rank",
            "stock_id",
            "stock_name",
            "foreign_held_shares",
            "foreign_held_ratio",
        ),
        source_urls=("https://www.tpex.org.tw/web/stock/3insti/qfii/qfii_result.php",),
    ),
    "tpex.total-return-index": Dataset(
        id="tpex.total-return-index",
        title="櫃買指數與報酬指數",
        group="tpex",
        description="TPEx index and total return index values for the month containing the requested date.",
        module="tw_stock_cli.crawlers.tpex.total_return_index",
        kind="date",
        returns=("date", "index", "total_return_index"),
        source_urls=(
            "https://www.tpex.org.tw/web/stock/iNdex_info/reward_index/ROE_result.php",
        ),
    ),
    "taifex.futures-daily": Dataset(
        id="taifex.futures-daily",
        title="期貨每日交易行情",
        group="taifex",
        description="TAIFEX daily futures market data.",
        module="tw_stock_cli.crawlers.taifex.futures_daily",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/dlFutDataDown",),
    ),
    "taifex.options-daily": Dataset(
        id="taifex.options-daily",
        title="選擇權每日交易行情",
        group="taifex",
        description="TAIFEX daily options market data.",
        module="tw_stock_cli.crawlers.taifex.options_daily",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "strike_price",
            "call_put",
            "close",
            "volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/dlOptDataDown",),
    ),
    "taifex.futures-tick": Dataset(
        id="taifex.futures-tick",
        title="期貨逐筆成交",
        group="taifex",
        description="TAIFEX futures tick data. This can be very large.",
        module="tw_stock_cli.crawlers.taifex.futures_tick",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "expiry_month_week",
            "trade_time",
            "trade_price",
            "trade_volume",
        ),
        source_urls=(
            "https://www.taifex.com.tw/file/taifex/Dailydownload/DailydownloadCSV/",
        ),
        notes="Large dataset. Use --limit for exploration.",
    ),
    "taifex.options-tick": Dataset(
        id="taifex.options-tick",
        title="選擇權逐筆成交",
        group="taifex",
        description="TAIFEX options tick data. This can be very large.",
        module="tw_stock_cli.crawlers.taifex.options_tick",
        kind="date",
        returns=(
            "trade_date",
            "contract",
            "strike_price",
            "expiry_month_week",
            "call_put",
            "trade_time",
            "trade_price",
        ),
        source_urls=(
            "https://www.taifex.com.tw/file/taifex/Dailydownload/OptionsDailydownloadCSV/",
        ),
        notes="Large dataset. Use --limit for exploration.",
    ),
    "taifex.futures-institutional": Dataset(
        id="taifex.futures-institutional",
        title="期貨三大法人未平倉",
        group="taifex",
        description="TAIFEX futures institutional investor positions and open interest.",
        module="tw_stock_cli.crawlers.taifex.futures_institutional",
        kind="date",
        returns=(
            "row_number",
            "contract_name",
            "investor_type",
            "trade_long_volume",
            "open_interest_long_volume",
        ),
        source_urls=("https://www.taifex.com.tw/cht/3/futContractsDate",),
    ),
    "taifex.fcm-futures-volume-day": Dataset(
        id="taifex.fcm-futures-volume-day",
        title="期貨商期貨成交量日盤",
        group="taifex",
        description="TAIFEX futures commission merchant futures trading volume, regular session.",
        module="tw_stock_cli.crawlers.taifex.fcm_futures_volume_day",
        kind="none",
        returns=("fcm_id", "fcm_name", "subtotal"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_FUT_day.csv",
        ),
    ),
    "taifex.fcm-futures-volume-night": Dataset(
        id="taifex.fcm-futures-volume-night",
        title="期貨商期貨成交量夜盤",
        group="taifex",
        description="TAIFEX futures commission merchant futures trading volume, night session.",
        module="tw_stock_cli.crawlers.taifex.fcm_futures_volume_night",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_FUT_night.csv",
        ),
    ),
    "taifex.fcm-options-volume-day": Dataset(
        id="taifex.fcm-options-volume-day",
        title="期貨商選擇權成交量日盤",
        group="taifex",
        description="TAIFEX futures commission merchant options trading volume, regular session.",
        module="tw_stock_cli.crawlers.taifex.fcm_options_volume_day",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_OPT_day.csv",
        ),
    ),
    "taifex.fcm-options-volume-night": Dataset(
        id="taifex.fcm-options-volume-night",
        title="期貨商選擇權成交量夜盤",
        group="taifex",
        description="TAIFEX futures commission merchant options trading volume, night session.",
        module="tw_stock_cli.crawlers.taifex.fcm_options_volume_night",
        kind="none",
        returns=("fcm_id", "fcm_name", "total", "market_share"),
        source_urls=(
            "https://www.taifex.com.tw/cht/7/getFCMFile?filename=Daily_OPT_night.csv",
        ),
    ),
    "mops.month-revenue": Dataset(
        id="mops.month-revenue",
        title="月營收",
        group="mops",
        description="MOPS monthly revenue by company.",
        module="tw_stock_cli.crawlers.mops.month_revenue",
        kind="mops-month",
        returns=("stock_id", "revenue", "revenue_year", "revenue_month"),
        source_urls=("https://mopsov.twse.com.tw/nas/t21/",),
    ),
    "mops.income-statement": Dataset(
        id="mops.income-statement",
        title="綜合損益表",
        group="mops",
        description="MOPS quarterly income statement summary tables.",
        module="tw_stock_cli.crawlers.mops.income_statement",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb04",),
    ),
    "mops.balance-sheet": Dataset(
        id="mops.balance-sheet",
        title="資產負債表",
        group="mops",
        description="MOPS quarterly balance sheet summary tables.",
        module="tw_stock_cli.crawlers.mops.balance_sheet",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb05",),
    ),
    "mops.cash-flow": Dataset(
        id="mops.cash-flow",
        title="現金流量表",
        group="mops",
        description="MOPS quarterly cash flow summary tables.",
        module="tw_stock_cli.crawlers.mops.cash_flow",
        kind="mops-quarter",
        returns=("multiple tables",),
        source_urls=("https://mopsov.twse.com.tw/mops/web/ajax_t163sb20",),
    ),
}


def list_datasets(group: str | None = None) -> list[Dataset]:
    datasets = sorted(DATASETS.values(), key=lambda dataset: dataset.id)
    if group:
        datasets = [dataset for dataset in datasets if dataset.group == group]
    return datasets


def get_dataset(dataset_id: str) -> Dataset:
    try:
        return DATASETS[dataset_id]
    except KeyError as exc:
        raise KeyError(f"Unknown dataset: {dataset_id}") from exc
