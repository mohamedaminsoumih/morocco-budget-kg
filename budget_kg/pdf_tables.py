"""Read the budget tables (Tableaux B, C, D) from a finance law PDF."""

import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import pdfplumber

from budget_kg.chapters import is_chapter_code

AMOUNT_PATTERN = re.compile(r"^\d{1,3}(?: \d{3})*$")
LEADER_DOTS = re.compile(r"\.{3,}")


@dataclass
class Label:
    text: str
    is_item: bool  # "- Personnel" is an item, "MINISTERE DE ..." is a heading


@dataclass
class TableRow:
    codes: list[str]
    labels: list[Label]
    amounts: list[list[str]]


def to_label(line: str) -> Label:
    """'- Personnel ..........' → Label('Personnel', is_item=True)."""
    is_item = line.strip().startswith("-")
    return Label(LEADER_DOTS.sub("", line).strip(" -"), is_item)


def parse_amount(text: str) -> int:
    """'42 710 520 000' → 42710520000; '-' or 'Mémoire' → 0."""
    text = text.strip()
    return int(text.replace(" ", "")) if AMOUNT_PATTERN.match(text) else 0


def _to_row(cells: list[str]) -> TableRow | None:
    """A table row that starts with chapter codes, or None."""
    codes = cells[0].split("\n") if cells else []
    if not codes or not all(is_chapter_code(code) for code in codes):
        return None
    labels = [to_label(line) for line in cells[1].split("\n")]
    amounts = [cell.split("\n") for cell in cells[2:]]
    return TableRow([c.strip() for c in codes], labels, amounts)


def all_table_rows(path: Path) -> Iterator[list[str]]:
    """Every row of every table in the PDF, as a list of cell texts."""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                for raw in table:
                    yield [(cell or "").strip() for cell in raw]


def read_budget_rows(path: Path) -> list[TableRow]:
    """All table rows that contain budget chapter codes."""
    rows = (_to_row(cells) for cells in all_table_rows(path))
    return [row for row in rows if row is not None]
