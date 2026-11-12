"""Project settings: paths and the finance law documents."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ONTOLOGY_FILE = PROJECT_ROOT / "ontology" / "budget.ttl"
GRAPH_FILE = PROJECT_ROOT / "output" / "budget_graph.ttl"
QUERIES_DIR = PROJECT_ROOT / "queries"
SHAPES_FILE = PROJECT_ROOT / "shapes" / "budget_shapes.ttl"

# Budget year → document type (French editions)
# LF = voted Loi de Finances, PLF = Projet de Loi de Finances (not voted yet)
DOCUMENTS = {
    2023: "LF",
    2024: "LF",
    2025: "LF",
    2026: "LF",
    2027: "PLF",
}


def document_path(year: int) -> Path:
    """data/raw/LF2026_fr.pdf, data/raw/PLF2027_fr.pdf..."""
    return RAW_DIR / f"{DOCUMENTS[year]}{year}_fr.pdf"
