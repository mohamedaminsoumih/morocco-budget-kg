"""Check the knowledge graph against the SHACL shapes.

Usage:
    python -m budget_kg.validate_graph
"""

import sys

from pyshacl import validate
from rdflib import Graph

from budget_kg.config import GRAPH_FILE, SHAPES_FILE


def main() -> None:
    graph = Graph().parse(GRAPH_FILE)
    shapes = Graph().parse(SHAPES_FILE)
    conforms, _, report = validate(graph, shacl_graph=shapes, inference="rdfs")
    if not conforms:
        print(report)
        sys.exit(1)
    print(f"Graph conforms to {SHAPES_FILE.name} ({len(graph):,} triples)")


if __name__ == "__main__":
    main()
