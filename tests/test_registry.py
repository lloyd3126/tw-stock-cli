from __future__ import annotations

from importlib import import_module

import pytest

from tw_stock_cli.registry import DATASETS
from tw_stock_cli.registry import get_dataset
from tw_stock_cli.registry import list_datasets
from tw_stock_cli.registry import normalize_roc_year
from tw_stock_cli.registry import require


def test_dataset_catalog_contains_expected_public_datasets() -> None:
    assert len(DATASETS) == 27
    assert set(DATASETS) >= {
        "twse.stock-price",
        "tpex.stock-price",
        "taifex.futures-daily",
        "taifex.fcm-futures-volume-day",
        "mops.month-revenue",
        "mops.income-statement",
    }


def test_dataset_ids_match_dataclass_ids() -> None:
    for dataset_id, dataset in DATASETS.items():
        assert dataset.id == dataset_id


def test_dataset_modules_are_importable_and_expose_crawler() -> None:
    for dataset in DATASETS.values():
        module = import_module(dataset.module)
        assert hasattr(module, "crawler"), dataset.module


def test_list_datasets_is_sorted_and_filterable_by_group() -> None:
    datasets = list_datasets()
    twse_datasets = list_datasets("twse")

    assert [dataset.id for dataset in datasets] == sorted(DATASETS)
    assert twse_datasets
    assert all(dataset.group == "twse" for dataset in twse_datasets)


def test_get_dataset_reports_unknown_dataset() -> None:
    with pytest.raises(KeyError, match="Unknown dataset"):
        get_dataset("unknown.dataset")


def test_require_rejects_missing_values() -> None:
    with pytest.raises(ValueError, match="Missing required parameter: date"):
        require({"date": ""}, "date")


def test_normalize_roc_year_accepts_roc_and_ad_years() -> None:
    assert normalize_roc_year(115) == 115
    assert normalize_roc_year(2026) == 115
