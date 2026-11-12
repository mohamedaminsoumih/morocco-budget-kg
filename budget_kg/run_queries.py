"""Run every SPARQL query in queries/ on the knowledge graph.

Usage:
    python -m budget_kg.run_queries
"""

import pandas as pd
from rdflib import Graph, Literal
from rdflib.query import ResultRow

from budget_kg.config import GRAPH_FILE, QUERIES_DIR

OUTPUT_DIR = GRAPH_FILE.parent / "query_results"


def run_query(graph: Graph, query: str) -> pd.DataFrame:
    result = graph.query(query)
    columns = [str(variable) for variable in result.vars or []]
    rows = [
        [cell.toPython() if isinstance(cell, Literal) else cell for cell in row]
        for row in result
        if isinstance(row, ResultRow)
    ]
    return pd.DataFrame(rows, columns=columns)


def main() -> None:
    graph = Graph().parse(GRAPH_FILE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pd.set_option("display.max_colwidth", 60)
    pd.set_option("display.width", 200)

    for path in sorted(QUERIES_DIR.glob("*.rq")):
        table = run_query(graph, path.read_text(encoding="utf-8"))
        table.to_csv(OUTPUT_DIR / f"{path.stem}.csv", index=False)
        print(f"\n=== {path.stem} ===")
        print(table.round(1).to_string(index=False))


if __name__ == "__main__":
    main()
