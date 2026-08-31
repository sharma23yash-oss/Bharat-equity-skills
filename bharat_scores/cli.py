"""Command line entry point.

    python -m bharat_scores examples/data/eicher-motors.json
    python -m bharat_scores examples/data/*.json --out reports/

Input is a JSON file shaped like :class:`~bharat_scores.models.Company`; see
``examples/data/`` for working files and ``docs/input-format.md`` for the
field reference.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .models import Company, FiscalYear
from .report import to_markdown


def load_company(path: Path) -> Company:
    """Build a Company from a JSON file, ignoring unknown keys with a warning."""
    raw = json.loads(path.read_text(encoding="utf-8"))

    valid_year_fields = set(FiscalYear.__dataclass_fields__)
    years: list[FiscalYear] = []
    for i, y in enumerate(raw.get("years", [])):
        unknown = set(y) - valid_year_fields
        if unknown:
            print(
                f"  warning: {path.name} year[{i}] has unknown field(s): "
                f"{', '.join(sorted(unknown))}",
                file=sys.stderr,
            )
        years.append(FiscalYear(**{k: v for k, v in y.items() if k in valid_year_fields}))

    if not years:
        raise ValueError(f"{path}: no 'years' array, or it is empty")

    return Company(
        name=raw.get("name", path.stem),
        ticker=raw.get("ticker", ""),
        sector=raw.get("sector", ""),
        is_financial=bool(raw.get("is_financial", False)),
        years=years,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bharat_scores",
        description="Forensic accounting scores for Indian listed companies.",
    )
    parser.add_argument("files", nargs="+", type=Path,
                        help="one or more company JSON files")
    parser.add_argument("--out", type=Path, default=None,
                        help="write <ticker>.md into this directory instead of stdout")
    args = parser.parse_args(argv)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)

    exit_code = 0
    for path in args.files:
        try:
            company = load_company(path)
            md = to_markdown(company)
        except Exception as exc:  # noqa: BLE001 — report and continue to next file
            print(f"error: {path}: {exc}", file=sys.stderr)
            exit_code = 1
            continue

        if args.out:
            slug = (company.ticker or company.name).replace(" ", "-").lower()
            dest = args.out / f"{slug}.md"
            dest.write_text(md, encoding="utf-8")
            print(f"wrote {dest}")
        else:
            print(md)
            print()

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
