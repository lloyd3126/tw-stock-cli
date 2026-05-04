from __future__ import annotations

import argparse
import json
import sys

import pandas as pd
import pytest

from tw_stock_cli import cli
from tw_stock_cli.registry import get_dataset


def run_cli(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], *args: str
):
    monkeypatch.setattr(sys, "argv", ["tw-stock", *args])
    cli.main()
    return capsys.readouterr()


def test_list_datasets_json_outputs_catalog_metadata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured = run_cli(
        monkeypatch, capsys, "list-datasets", "--group", "twse", "--json"
    )
    payload = json.loads(captured.out)

    assert payload
    assert all(dataset["group"] == "twse" for dataset in payload)
    assert {"id", "title", "required_params", "source_urls"} <= set(payload[0])


def test_describe_json_outputs_single_dataset_metadata(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    captured = run_cli(monkeypatch, capsys, "describe", "twse.stock-price", "--json")
    payload = json.loads(captured.out)

    assert payload["id"] == "twse.stock-price"
    assert payload["required_params"] == ["date"]
    assert payload["returns"] == [
        "stock_id",
        "stock_name",
        "open",
        "high",
        "low",
        "close",
        "date",
    ]


def test_fetch_schema_only_does_not_fetch_network(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_fetch(self, params):
        raise AssertionError(f"unexpected fetch: {params}")

    monkeypatch.setattr("tw_stock_cli.registry.Dataset.fetch", fail_fetch)

    captured = run_cli(
        monkeypatch,
        capsys,
        "fetch",
        "twse.stock-price",
        "--schema-only",
        "--format",
        "json",
    )
    payload = json.loads(captured.out)

    assert payload["id"] == "twse.stock-price"


def test_fetch_source_url_only_does_not_fetch_network(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail_fetch(self, params):
        raise AssertionError(f"unexpected fetch: {params}")

    monkeypatch.setattr("tw_stock_cli.registry.Dataset.fetch", fail_fetch)

    captured = run_cli(
        monkeypatch,
        capsys,
        "fetch",
        "twse.stock-price",
        "--source-url-only",
        "--format",
        "json",
    )
    payload = json.loads(captured.out)

    assert payload["dataset"] == "twse.stock-price"
    assert payload["source_urls"]


def test_params_from_args_preserves_mops_arguments() -> None:
    args = argparse.Namespace(
        date=None,
        year=2026,
        month=3,
        quarter=None,
        market="sii",
        foreign=1,
    )

    assert cli.params_from_args(args) == {
        "date": None,
        "year": 2026,
        "month": 3,
        "quarter": None,
        "market": "sii",
        "foreign": 1,
    }


def test_transform_output_applies_columns_and_limit() -> None:
    frame = pd.DataFrame(
        [
            {"stock_id": "2330", "stock_name": "台積電", "close": "780"},
            {"stock_id": "2317", "stock_name": "鴻海", "close": "155"},
        ]
    )

    result = cli.transform_output(frame, columns="stock_id,close", limit=1)

    assert list(result.columns) == ["stock_id", "close"]
    assert result.to_dict("records") == [{"stock_id": "2330", "close": "780"}]


def test_transform_output_rejects_missing_column() -> None:
    frame = pd.DataFrame([{"stock_id": "2330"}])

    with pytest.raises(cli.CliError) as exc:
        cli.transform_output(frame, columns="missing", limit=None)

    assert exc.value.code == "INVALID_COLUMN"


def test_to_jsonable_handles_multi_table_outputs() -> None:
    output = [
        pd.DataFrame([{"公司代號": "2330"}]),
        pd.DataFrame([{"公司代號": "2317", "eps": None}]),
    ]

    payload = cli.to_jsonable(output)

    assert payload == {
        "tables": [
            {
                "table_index": 0,
                "columns": ["公司代號"],
                "rows": [{"公司代號": "2330"}],
            },
            {
                "table_index": 1,
                "columns": ["公司代號", "eps"],
                "rows": [{"公司代號": "2317", "eps": None}],
            },
        ]
    }


def test_emit_rejects_csv_for_multi_table_dataset() -> None:
    dataset = get_dataset("mops.income-statement")

    with pytest.raises(cli.CliError) as exc:
        cli.emit([pd.DataFrame([{"a": 1}])], "csv", None, dataset)

    assert exc.value.code == "UNSUPPORTED_FORMAT"


def test_validation_result_reports_empty_frame_as_not_ok() -> None:
    dataset = get_dataset("twse.stock-price")
    result = cli.validation_result(dataset, pd.DataFrame(columns=["stock_id"]))

    assert result["ok"] is False
    assert result["rows"] == 0
    assert result["tables"] == 1
