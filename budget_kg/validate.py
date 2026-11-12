"""Check the extracted lines against the totals printed in the law.

Each table ends with an official total (operating, investment, debt).
If our sum differs, a line was missed or misread, and we stop.
"""

from pathlib import Path

import pandas as pd

from budget_kg.chapters import is_chapter_code
from budget_kg.pdf_tables import AMOUNT_PATTERN, all_table_rows, parse_amount

# Budget title → prefix of its budget lines
TITLES = {
    "operating": "operating_",
    "investment": "investment",
    "debt": "debt_",
}


def _is_total_row(cells: list[str]) -> bool:
    """A row with amounts but no chapter code is a total row."""
    lines = [line for cell in cells for line in cell.split("\n")]
    has_code = any(is_chapter_code(line) for line in lines)
    has_amount = any(AMOUNT_PATTERN.match(cell) for cell in cells)
    return has_amount and not has_code


def official_totals(path: Path) -> set[int]:
    """The largest amount of each total row in the document."""
    totals = set()
    for cells in all_table_rows(path):
        if _is_total_row(cells):
            amounts = [parse_amount(c) for c in cells if AMOUNT_PATTERN.match(c)]
            totals.add(max(amounts))
    return totals


def check_totals(lines: pd.DataFrame, path: Path) -> None:
    """Operating, investment and debt sums must each match an official total."""
    totals = official_totals(path)
    lines = lines.assign(total=lines["payment_mad"] + lines["commitment_mad"])

    for title, prefix in TITLES.items():
        part = lines[lines["budget_line"].str.startswith(prefix)]
        # Investment totals include commitment credits for next years
        column = "total" if title == "investment" else "payment_mad"
        computed = int(part[column].sum())
        if computed not in totals:
            raise ValueError(
                f"{path.name}: {title} sum {computed:,} "
                f"matches no official total {sorted(totals)}"
            )
