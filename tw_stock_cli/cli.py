"""Command-line interface for discovering, fetching, and validating datasets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from .registry import Dataset, get_dataset, list_datasets


class CliError(Exception):
    def __init__(self, code: str, message: str, dataset: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.dataset = dataset


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "list-datasets":
            command_list(args)
        elif args.command == "describe":
            command_describe(args)
        elif args.command == "fetch":
            command_fetch(args)
        elif args.command == "validate":
            command_validate(args)
        else:
            parser.print_help()
    except CliError as exc:
        print_error(
            exc,
            json_output=getattr(args, "json", False)
            or getattr(args, "format", "") == "json",
        )
        sys.exit(1)
    except KeyError as exc:
        print_error(
            CliError("UNKNOWN_DATASET", str(exc).strip("'")),
            json_output=getattr(args, "json", False),
        )
        sys.exit(1)
    except ValueError as exc:
        print_error(
            CliError("INVALID_PARAMETER", str(exc), getattr(args, "dataset", None)),
            json_output=getattr(args, "json", False),
        )
        sys.exit(1)
    except Exception as exc:
        print_error(
            CliError("FETCH_ERROR", str(exc), getattr(args, "dataset", None)),
            json_output=getattr(args, "json", False),
        )
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tw-stock",
        description="Fetch Taiwan market datasets for humans and AI agents.",
    )
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser(
        "list-datasets", help="List available dataset IDs."
    )
    list_parser.add_argument(
        "--group",
        choices=["twse", "tpex", "taifex", "mops"],
        help="Filter by data source group.",
    )
    list_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )

    describe_parser = subparsers.add_parser("describe", help="Describe one dataset.")
    describe_parser.add_argument("dataset")
    describe_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )

    fetch_parser = subparsers.add_parser("fetch", help="Fetch a dataset.")
    add_dataset_args(fetch_parser)
    fetch_parser.add_argument(
        "--format",
        choices=["table", "json", "jsonl", "csv", "parquet"],
        default="table",
    )
    fetch_parser.add_argument(
        "--output", help="Write output to a file instead of stdout."
    )
    fetch_parser.add_argument(
        "--limit", type=int, help="Return only the first N rows after fetching."
    )
    fetch_parser.add_argument("--columns", help="Comma-separated columns to keep.")
    fetch_parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Print dataset schema metadata without fetching.",
    )
    fetch_parser.add_argument(
        "--source-url-only",
        action="store_true",
        help="Print source URL templates without fetching.",
    )

    validate_parser = subparsers.add_parser(
        "validate", help="Fetch and check that a dataset returns rows/tables."
    )
    add_dataset_args(validate_parser)
    validate_parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )

    return parser


def add_dataset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("dataset")
    parser.add_argument("--date", help="Trading date in YYYY-MM-DD format.")
    parser.add_argument(
        "--year",
        type=int,
        help="MOPS year. Accepts ROC year such as 115 or AD year such as 2026.",
    )
    parser.add_argument("--month", type=int, help="MOPS month number.")
    parser.add_argument(
        "--quarter", type=int, choices=[1, 2, 3, 4], help="MOPS quarter number."
    )
    parser.add_argument(
        "--market",
        default="sii",
        choices=["sii", "otc", "rotc", "pub"],
        help="MOPS market/type. Default: sii.",
    )
    parser.add_argument(
        "--foreign",
        type=int,
        choices=[0, 1],
        default=0,
        help="MOPS monthly revenue foreign flag. Default: 0.",
    )


def command_list(args: argparse.Namespace) -> None:
    datasets = list_datasets(args.group)
    if args.json:
        print(
            json.dumps(
                [dataset_metadata(dataset) for dataset in datasets],
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    rows = [
        (dataset.id, dataset.title, dataset.group, required_params(dataset))
        for dataset in datasets
    ]
    print(format_table(rows, ("dataset", "title", "group", "required params")))


def command_describe(args: argparse.Namespace) -> None:
    dataset = get_dataset(args.dataset)
    metadata = dataset_metadata(dataset)
    if args.json:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        return

    print(f"{dataset.id} - {dataset.title}")
    print(dataset.description)
    print(f"group: {dataset.group}")
    print(f"required params: {required_params(dataset)}")
    print(f"returns: {', '.join(dataset.returns)}")
    if dataset.notes:
        print(f"notes: {dataset.notes}")
    print("source URLs:")
    for url in dataset.source_urls:
        print(f"- {url}")


def command_fetch(args: argparse.Namespace) -> None:
    dataset = get_dataset(args.dataset)
    if args.schema_only:
        print(json.dumps(dataset_metadata(dataset), ensure_ascii=False, indent=2))
        return
    if args.source_url_only:
        print(
            json.dumps(
                {"dataset": dataset.id, "source_urls": dataset.source_urls},
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    params = params_from_args(args)
    output = dataset.fetch(params)
    output = transform_output(output, columns=args.columns, limit=args.limit)
    emit(output, args.format, args.output, dataset)


def command_validate(args: argparse.Namespace) -> None:
    dataset = get_dataset(args.dataset)
    params = params_from_args(args)
    output = dataset.fetch(params)
    result = validation_result(dataset, output)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    status = "ok" if result["ok"] else "failed"
    print(f"{status}: {dataset.id}")
    print(f"rows: {result.get('rows', 0)}")
    print(f"tables: {result.get('tables', 0)}")
    print(f"columns: {', '.join(result.get('columns', []))}")


def params_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "date": args.date,
        "year": args.year,
        "month": args.month,
        "quarter": args.quarter,
        "market": args.market,
        "foreign": args.foreign,
    }


def transform_output(
    output: pd.DataFrame | list[pd.DataFrame],
    columns: str | None,
    limit: int | None,
) -> pd.DataFrame | list[pd.DataFrame]:
    keep_columns = (
        [column.strip() for column in columns.split(",")] if columns else None
    )

    def transform_frame(df: pd.DataFrame) -> pd.DataFrame:
        result = df
        if keep_columns:
            missing = [
                column for column in keep_columns if column not in result.columns
            ]
            if missing:
                raise CliError(
                    "INVALID_COLUMN", f"Columns not found: {', '.join(missing)}"
                )
            result = result[keep_columns]
        if limit is not None:
            result = result.head(limit)
        return result

    if isinstance(output, list):
        return [transform_frame(df) for df in output]
    return transform_frame(output)


def emit(
    output: pd.DataFrame | list[pd.DataFrame],
    output_format: str,
    output_path: str | None,
    dataset: Dataset,
) -> None:
    if output_format in {"csv", "parquet"} and isinstance(output, list):
        raise CliError(
            "UNSUPPORTED_FORMAT",
            "CSV and parquet are not supported for multi-table datasets. Use json or jsonl.",
            dataset.id,
        )

    text: str | None = None
    if output_format == "table":
        text = render_table_output(output)
    elif output_format == "json":
        text = json.dumps(to_jsonable(output), ensure_ascii=False, indent=2)
    elif output_format == "jsonl":
        text = to_jsonl(output)
    elif output_format == "csv":
        frame = ensure_frame(output)
        if output_path:
            frame.to_csv(output_path, index=False)
            return
        text = frame.to_csv(index=False)
    elif output_format == "parquet":
        if not output_path:
            raise CliError(
                "OUTPUT_REQUIRED", "Parquet output requires --output.", dataset.id
            )
        frame = ensure_frame(output)
        frame.to_parquet(output_path, index=False)
        return

    if output_path:
        Path(output_path).write_text(text or "", encoding="utf-8")
    else:
        print(text or "")


def render_table_output(output: pd.DataFrame | list[pd.DataFrame]) -> str:
    if isinstance(output, list):
        chunks = []
        for index, frame in enumerate(output):
            chunks.append(
                f"table {index}: {len(frame)} rows x {len(frame.columns)} columns"
            )
            chunks.append(frame.head(20).to_string(index=False))
        return "\n\n".join(chunks)
    return output.head(50).to_string(index=False)


def ensure_frame(output: pd.DataFrame | list[pd.DataFrame]) -> pd.DataFrame:
    if isinstance(output, list):
        raise CliError("UNSUPPORTED_FORMAT", "Expected a single-table dataset.")
    return output


def to_jsonable(output: pd.DataFrame | list[pd.DataFrame]) -> dict[str, Any]:
    if isinstance(output, list):
        return {
            "tables": [
                {
                    "table_index": index,
                    "columns": [str(column) for column in frame.columns],
                    "rows": clean_frame(frame).to_dict("records"),
                }
                for index, frame in enumerate(output)
            ]
        }
    return {
        "columns": [str(column) for column in output.columns],
        "rows": clean_frame(output).to_dict("records"),
    }


def to_jsonl(output: pd.DataFrame | list[pd.DataFrame]) -> str:
    lines = []
    if isinstance(output, list):
        for table_index, frame in enumerate(output):
            clean = clean_frame(frame)
            for row in clean.to_dict("records"):
                lines.append(
                    json.dumps({"table_index": table_index, **row}, ensure_ascii=False)
                )
    else:
        clean = clean_frame(output)
        for row in clean.to_dict("records"):
            lines.append(json.dumps(row, ensure_ascii=False))
    return "\n".join(lines)


def clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    return frame.astype(object).where(pd.notna(frame), None)


def validation_result(
    dataset: Dataset, output: pd.DataFrame | list[pd.DataFrame]
) -> dict[str, Any]:
    if isinstance(output, list):
        row_count = sum(len(frame) for frame in output)
        columns = [str(column) for frame in output for column in frame.columns][:30]
        return {
            "ok": bool(output) and row_count > 0,
            "dataset": dataset.id,
            "tables": len(output),
            "rows": row_count,
            "columns": columns,
            "source_urls": dataset.source_urls,
        }
    return {
        "ok": len(output) > 0,
        "dataset": dataset.id,
        "tables": 1,
        "rows": len(output),
        "columns": [str(column) for column in output.columns],
        "source_urls": dataset.source_urls,
    }


def dataset_metadata(dataset: Dataset) -> dict[str, Any]:
    return {
        "id": dataset.id,
        "title": dataset.title,
        "group": dataset.group,
        "description": dataset.description,
        "required_params": required_params(dataset).split(", ")
        if required_params(dataset)
        else [],
        "optional_params": optional_params(dataset),
        "returns": list(dataset.returns),
        "source_urls": list(dataset.source_urls),
        "notes": dataset.notes,
    }


def required_params(dataset: Dataset) -> str:
    if dataset.kind == "date":
        return "date"
    if dataset.kind == "mops-month":
        return "year, month"
    if dataset.kind == "mops-quarter":
        return "year, quarter"
    return ""


def optional_params(dataset: Dataset) -> list[str]:
    if dataset.kind == "mops-month":
        return ["market", "foreign"]
    if dataset.kind == "mops-quarter":
        return ["market"]
    return []


def format_table(rows: list[tuple[Any, ...]], headers: tuple[str, ...]) -> str:
    all_rows = [headers] + [tuple(str(value) for value in row) for row in rows]
    widths = [
        max(len(str(row[index])) for row in all_rows) for index in range(len(headers))
    ]
    lines = []
    for row_index, row in enumerate(all_rows):
        lines.append(
            "  ".join(
                str(value).ljust(widths[index]) for index, value in enumerate(row)
            )
        )
        if row_index == 0:
            lines.append("  ".join("-" * width for width in widths))
    return "\n".join(lines)


def print_error(error: CliError, json_output: bool = False) -> None:
    payload = {
        "ok": False,
        "error_code": error.code,
        "message": error.message,
    }
    if error.dataset:
        payload["dataset"] = error.dataset

    if json_output:
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
    else:
        print(f"{error.code}: {error.message}", file=sys.stderr)


if __name__ == "__main__":
    main()
