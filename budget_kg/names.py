"""Normalize institution names so that only real renamings are detected.

The laws write the same name differently from one year to the next:
' vs ’, É vs E, lowercase vs uppercase, typos in spaces. The key removes
these differences; the original name is kept as the label.
"""

import re
import unicodedata

APOSTROPHES = str.maketrans({"’": "'", "‘": "'", "`": "'"})


def name_key(name: str) -> str:
    """'Ministère de l’Économie' → 'MINISTERE DE L'ECONOMIE'."""
    text = name.translate(APOSTROPHES)
    decomposed = unicodedata.normalize("NFKD", text)
    no_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", no_accents).strip().upper()
