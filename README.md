# tw-stock-cli

透過一個小型 Python CLI，從 TWSE、TPEx、TAIFEX 與 MOPS 抓取台灣市場公開資料。

## 涵蓋資料

- TWSE 上市股票每日價格、股票清單、本益比/殖利率/PBR、三大法人買賣超、融資融券、外資持股與報酬指數資料。
- TPEx 上櫃股票每日價格、股票清單、本益比/殖利率/PBR、三大法人買賣超、融資融券、外資持股與指數資料。
- TAIFEX 期貨與選擇權日行情、逐筆成交、三大法人部位與期貨商成交量。
- MOPS 月營收、彙總三表、單一公司詳細四表、公司基本資料、財報/年報/關係企業三書表電子書、主要股東關係、永續報告書、企業 ESG 資訊揭露、員工薪資福利、員工福利政策、董事會治理、公司治理組織架構、功能性委員會、股利分派、除權息公告、庫藏股、私募、取得或處分資產、資金貸與、背書保證、關係人交易、董監事酬金、經理人酬勞、股權分散、法說會、股東會、重大訊息、內部人股權異動、持股餘額、轉讓申報與質權設定資料。

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
uv run tw-stock fetch mops.company-cash-flow --stock-id 2395 --year 2025 --quarter 4 --format jsonl
uv run tw-stock fetch mops.company-basic-info --stock-id 2395 --market sii --format json
uv run tw-stock fetch mops.treasury-stock-buyback --stock-id 1101 --market sii --limit 2 --format json
uv run tw-stock fetch mops.private-placement --stock-id 1316 --market sii --limit 5 --format json
uv run tw-stock fetch mops.asset-acquisition-disposal --stock-id 8011 --year 2024 --month 9 --market sii --format json
uv run tw-stock fetch mops.asset-acquisition-disposal-financial --stock-id 8011 --year 2024 --month 9 --market sii --format json
uv run tw-stock fetch mops.fund-lending --stock-id 1101 --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.endorsement-guarantee --stock-id 1101 --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.related-party-transaction --stock-id 8011 --year 2024 --month 9 --market sii --limit 5 --format json
uv run tw-stock fetch mops.related-party-transaction-difference --stock-id 3162 --year 2025 --quarter 1 --market otc --format json
uv run tw-stock fetch mops.director-supervisor-remuneration --year 2024 --market sii --limit 5 --format json
uv run tw-stock fetch mops.financial-report-electronic-book --stock-id 2395 --year 2024 --market all --format json
uv run tw-stock fetch mops.annual-report-electronic-book --stock-id 2395 --year 2024 --market all --format json
uv run tw-stock fetch mops.related-company-reports --stock-id 2395 --year 2024 --market all --format json
uv run tw-stock fetch mops.major-shareholder-relationship --stock-id 2395 --year 2024 --market sii --format json
uv run tw-stock fetch mops.sustainability-report --stock-id 2395 --year 2024 --market sii --format json
uv run tw-stock fetch mops.employee-benefit-expense --year 2024 --market sii --limit 5 --format json
uv run tw-stock fetch mops.employee-welfare-policy --stock-id 2395 --year 2025 --market all --format json
uv run tw-stock fetch mops.esg-company-disclosure --stock-id 2395 --year 2024 --market sii --format json
uv run tw-stock fetch mops.full-time-employee-salary --year 2024 --market sii --limit 5 --format json
uv run tw-stock fetch mops.independent-director-profile --market sii --limit 5 --format json
uv run tw-stock fetch mops.board-attendance-training --stock-id 2395 --market sii --format json
uv run tw-stock fetch mops.functional-committee --market sii --committee 4 --limit 5 --format json
uv run tw-stock fetch mops.company-governance-structure --stock-id 2395 --market sii --format json
uv run tw-stock fetch mops.manager-compensation-distribution --stock-id 2395 --year 2024 --market sii --format json
uv run tw-stock fetch mops.shareholding-distribution --stock-id 2395 --year 2024 --market sii --format json
uv run tw-stock fetch mops.dividend-distribution --stock-id 2395 --year 2025 --format json
uv run tw-stock fetch mops.ex-dividend-announcement --stock-id 2395 --year 2025 --market sii --format json
uv run tw-stock fetch mops.investor-conference --stock-id 2395 --year 2025 --market sii --format jsonl
uv run tw-stock fetch mops.shareholder-meeting --stock-id 2395 --year 2025 --market sii --format json
uv run tw-stock fetch mops.insider-shareholding-change --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.insider-shareholding-detail --stock-id 2395 --year 2025 --month 3 --market sii --format jsonl
uv run tw-stock fetch mops.insider-holding-company-list --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.insider-holding-detail --stock-id 2395 --year 2025 --month 3 --market sii --format jsonl
uv run tw-stock fetch mops.insider-transfer-declaration-summary --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.insider-transfer-untransferred-summary --year 2025 --month 3 --market sii --format json
uv run tw-stock fetch mops.insider-pledge-summary --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.insider-pledge-ratio-summary --year 2025 --month 3 --market sii --limit 5 --format json
uv run tw-stock fetch mops.material-info --stock-id 2395 --year 2025 --format jsonl
uv run tw-stock fetch mops.material-info-detail --stock-id 2395 --market sii --seq-no 4 --spoke-date 20250227 --spoke-time 143238 --format json
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

MOPS 單一公司詳細財報會以 `item` 保留來源會計項目，並依來源表頭產生動態期間欄位，例如 `114年度_amount` 或 `114年12月31日_percent`。這類資料可用來取得彙總表沒有的現金流量表細項，例如取得不動產、廠房及設備或取得無形資產。權益變動表因來源同時提供比較年度，JSON 輸出會回傳多張表。

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
