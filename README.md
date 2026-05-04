# tw-stock-cli

透過一個小型 Python CLI，從 TWSE、TPEx、TAIFEX 與 MOPS 抓取台灣市場公開資料。

## 涵蓋資料

- TWSE 上市股票每日價格、股票清單、本益比/殖利率/PBR、三大法人買賣超、融資融券、外資持股與報酬指數資料。
- TPEx 上櫃股票每日價格、股票清單、本益比/殖利率/PBR、三大法人買賣超、融資融券、外資持股與指數資料。
- TAIFEX 期貨與選擇權日行情、逐筆成交、三大法人部位與期貨商成交量。
- MOPS 月營收、綜合損益表、資產負債表與現金流量表。

## 需求

- Python 3.10+
- `uv`
- 可連線至台灣交易所、櫃買中心、期交所與公開資訊觀測站端點

## 使用方式

在此 repository 中使用 `uv` 執行指令：

```sh
uv run tw-stock list-datasets
uv run tw-stock describe twse.stock-price
uv run tw-stock fetch twse.stock-price --date 2026-04-30 --format jsonl
uv run tw-stock validate twse.stock-price --date 2026-04-30 --json
```

使用 `--format` 選擇輸出格式，可用格式包含 `table`、`json`、`jsonl`、`csv` 或 `parquet`。

使用 `--output` 匯出到檔案：

```sh
uv run tw-stock fetch tpex.stock-price --date 2026-04-30 --format csv --output tpex-stock-price.csv
```

## 查詢資料集

```sh
uv run tw-stock list-datasets --json
uv run tw-stock list-datasets --group twse
uv run tw-stock list-datasets --group tpex
uv run tw-stock list-datasets --group taifex
uv run tw-stock list-datasets --group mops
```

每個資料集的中文簡介、範例指令、主要欄位與常見用途整理在 [資料集指南](docs/datasets.md)。

## 專案結構

Crawler 模組放在 `tw_stock_cli/crawlers`，並依照資料來源分組：

```text
tw_stock_cli/
  cli.py                  # CLI 指令與輸出格式
  registry.py             # 資料集 catalog 與 crawler dispatch
  crawlers/
    common.py             # 共用 HTTP 與 DataFrame helper
    twse/                 # TWSE 上市市場資料集
    tpex/                 # TPEx 上櫃市場資料集
    taifex/               # TAIFEX 期貨與選擇權資料集
    mops/                 # MOPS 財務申報資料集
```

每個來源資料夾底下的模組名稱會描述資料集主題，例如 `stock_price.py`、`institutional_trade.py` 或 `month_revenue.py`。

## 欄位命名

Crawler 輸出會將共通欄位正規化為英文 `snake_case`，例如 `stock_id`、`stock_name`、`date`、`open`、`high`、`low`、`close` 與 `volume`。MOPS 財報中的來源特定會計科目會保留中文，但共用識別欄位仍會正規化為 `stock_id` 與 `stock_name`。

## 測試

執行不會發送即時交易所請求的快速測試：

```sh
uv run pytest
```

Live smoke tests 預設會略過，因為交易所端點可能較慢或暫時不可用。若要確認目前資料來源是否可用，可以明確執行：

```sh
TW_STOCK_LIVE_TESTS=1 uv run pytest tests/test_live_smoke.py
```

## 注意事項

交易所端點的回應格式可能會變動。若要建立報表或供使用者依賴的匯出流程，建議先執行 `validate`。

逐筆成交資料集可能很大。探索資料時建議搭配 `--limit`：

```sh
uv run tw-stock fetch taifex.futures-tick --date 2026-04-30 --limit 20 --format jsonl
```
