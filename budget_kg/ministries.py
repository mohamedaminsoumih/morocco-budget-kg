"""Find the ministry name for each chapter code in a table row.

Operating tables list a ministry heading followed by its lines:
    MINISTERE DE L'INTERIEUR        (heading, may span 2 lines)
    - Personnel                     (item, one per chapter code)
    - Matériel et Dépenses Diverses
Investment and debt tables have one chapter per row, the label is the name.
"""

from budget_kg.chapters import parse_chapter
from budget_kg.pdf_tables import Label, TableRow


def _headings(labels: list[Label]) -> list[str]:
    """Join consecutive heading lines into one name each."""
    headings: list[str] = []
    previous_was_heading = False
    for label in labels:
        if label.is_item:
            previous_was_heading = False
        elif previous_was_heading:
            headings[-1] = f"{headings[-1]} {label.text}"
        else:
            headings.append(label.text)
            previous_was_heading = True
    return headings


def names_by_code(row: TableRow) -> dict[str, str]:
    """Chapter code → name of its ministry or institution."""
    if len(row.codes) == 1:
        return {row.codes[0]: " ".join(label.text for label in row.labels)}

    # One heading per ministry, in the order the ministries appear
    ministry_codes = [parse_chapter(code).ministry_code for code in row.codes]
    ministries = list(dict.fromkeys(ministry_codes))
    name_of = dict(zip(ministries, _headings(row.labels)))
    return {
        code: name_of.get(ministry, "")
        for code, ministry in zip(row.codes, ministry_codes)
    }
