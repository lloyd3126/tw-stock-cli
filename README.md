# tw-stock-cli

Fetch Taiwan market datasets from TWSE, TPEx, TAIFEX, and MOPS through a small Python CLI.

## What It Covers

- TWSE listed stock prices, stock lists, PER/dividend/PBR, institutional trades, margin trades, foreign holdings, and total return index data.
- TPEx OTC stock prices, stock lists, PER/dividend/PBR, institutional trades, margin trades, foreign holdings, and index data.
- TAIFEX futures and options daily data, tick data, institutional positions, and FCM trading volume.
- MOPS monthly revenue, income statements, balance sheets, and cash flow statements.

## Requirements

- Python 3.10+
- `uv`
- Network access to Taiwan exchange and MOPS endpoints

## Usage

Run commands from this repository with `uv`:

```sh
uv run tw-stock list-datasets
uv run tw-stock describe twse.stock-price
uv run tw-stock fetch twse.stock-price --date 2026-04-30 --format jsonl
uv run tw-stock validate twse.stock-price --date 2026-04-30 --json
```

Use `--format` to choose `table`, `json`, `jsonl`, `csv`, or `parquet`.

Write exports with `--output`:

```sh
uv run tw-stock fetch tpex.stock-price --date 2026-04-30 --format csv --output tpex-stock-price.csv
```

## Dataset Discovery

```sh
uv run tw-stock list-datasets --json
uv run tw-stock list-datasets --group twse
uv run tw-stock list-datasets --group tpex
uv run tw-stock list-datasets --group taifex
uv run tw-stock list-datasets --group mops
```

## Source Layout

Crawler modules live under `tw_stock_cli/crawlers` and are grouped by data source:

```text
tw_stock_cli/
  cli.py                  # CLI commands and output formatting
  registry.py             # dataset catalog and crawler dispatch
  crawlers/
    common.py             # shared HTTP and DataFrame helpers
    twse/                 # TWSE listed-market datasets
    tpex/                 # TPEx OTC-market datasets
    taifex/               # TAIFEX futures and options datasets
    mops/                 # MOPS financial disclosure datasets
```

Inside each source folder, module names describe the dataset topic, such as `stock_price.py`, `institutional_trade.py`, or `month_revenue.py`.

## Testing

Run the fast test suite without live exchange requests:

```sh
uv run pytest
```

Live smoke tests are skipped by default because exchange endpoints can be slow or temporarily unavailable. Run them explicitly when you want to verify current source availability:

```sh
TW_STOCK_LIVE_TESTS=1 uv run pytest tests/test_live_smoke.py
```

## Notes

Exchange endpoints can change response shapes. For reliable workflows, run `validate` before building reports or exports that users rely on.

Tick datasets can be large. Use `--limit` when exploring:

```sh
uv run tw-stock fetch taifex.futures-tick --date 2026-04-30 --limit 20 --format jsonl
```
