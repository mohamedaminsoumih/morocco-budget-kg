"""Meaning of a budget chapter code, e.g. 1.2.1.1.0.13.000.

1.2 . 1 . 1 . 0 . 13 . 000
      |   |       |
      |   |       └── ministry or institution (13 = Finance)
      |   └────────── budget line inside the title (1 = staff...)
      └────────────── title (1 = operating, 2 = investment, 3 = debt)
"""

import re
from dataclasses import dataclass

CHAPTER_PATTERN = re.compile(r"^1\.2\.([123])\.(\d)\.0\.(\d{2})\.000$")

# (title, line) → budget line identifier used in the ontology
BUDGET_LINES = {
    ("1", "1"): "operating_staff",
    ("1", "2"): "operating_equipment",
    ("1", "3"): "operating_common_charges",
    ("1", "4"): "operating_unforeseen",
    ("1", "5"): "operating_tax_refunds",
    ("2", "2"): "investment",
    ("2", "3"): "investment_common_charges",
    ("3", "1"): "debt_interest",
    ("3", "2"): "debt_amortization",
}


@dataclass(frozen=True)
class Chapter:
    code: str
    budget_line: str
    ministry_code: str


def is_chapter_code(text: str) -> bool:
    return CHAPTER_PATTERN.match(text.strip()) is not None


def parse_chapter(code: str) -> Chapter:
    match = CHAPTER_PATTERN.match(code.strip())
    if match is None:
        raise ValueError(f"Not a budget chapter code: {code}")
    title, line, ministry = match.groups()
    return Chapter(code.strip(), BUDGET_LINES[(title, line)], ministry)
