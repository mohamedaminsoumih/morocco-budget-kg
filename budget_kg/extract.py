"""Extract every budget line of every finance law into one CSV file.

Usage:
    python -m budget_kg.extract
"""

import pandas as pd

from budget_kg.chapters import parse_chapter
from budget_kg.config import DOCUMENTS, PROCESSED_DIR, document_path
from budget_kg.ministries import names_by_code
from budget_kg.pdf_tables import TableRow, parse_amount, read_budget_rows
from budget_kg.validate import check_totals


def _amounts(row: TableRow, position: int) -> tuple[int, int]:
    """(payment credits, commitment credits) of the n-th code in the row.

    Operating and debt rows have one amount; investment rows have
    payment credits, commitment credits for next years, and a total.
    """
    values = [column[position] for column in row.amounts if position < len(column)]
    payment = parse_amount(values[0]) if values else 0
    commitment = parse_amount(values[1]) if len(values) >= 3 else 0
    return payment, commitment


def extract_year(year: int, law: str) -> pd.DataFrame:
    records = {}
    for row in read_budget_rows(document_path(year)):
        names = names_by_code(row)
        for position, code in enumerate(row.codes):
            if code in records:  # some pages repeat a table
                continue
            chapter = parse_chapter(code)
            payment, commitment = _amounts(row, position)
            records[code] = {
                "year": year,
                "law": law,
                "chapter_code": code,
                "ministry_code": chapter.ministry_code,
                "budget_line": chapter.budget_line,
                "payment_mad": payment,
                "commitment_mad": commitment,
                "ministry_name": names[code],
            }
    return pd.DataFrame(records.values())


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    years = []
    for year, law in DOCUMENTS.items():
        lines = extract_year(year, law)
        check_totals(lines, document_path(year))
        years.append(lines)
        print(f"{year} ({law}): {len(lines)} budget lines, totals match")

    output = PROCESSED_DIR / "budget_lines.csv"
    pd.concat(years).to_csv(output, index=False)
    print(f"→ {output.relative_to(PROCESSED_DIR.parent.parent)}")


if __name__ == "__main__":
    main()
