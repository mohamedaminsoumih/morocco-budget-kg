"""Turn the extracted budget lines into an RDF knowledge graph.

Usage:
    python -m budget_kg.build_graph
"""

import pandas as pd
from rdflib import RDF, RDFS, XSD, Graph, Literal, URIRef

from budget_kg.config import GRAPH_FILE, ONTOLOGY_FILE, PROCESSED_DIR
from budget_kg.names import name_key
from budget_kg.namespaces import BUD, DATA

MINISTRY_PREFIX = "MINISTERE"


def institution_uri(code: str) -> URIRef:
    return DATA[f"institution/{code}"]


def law_uri(law: str, year: int) -> URIRef:
    return DATA[f"law/{law}{year}"]


def add_laws(graph: Graph, lines: pd.DataFrame) -> None:
    for row in lines.drop_duplicates(["year", "law"]).to_dict("records"):
        law, year = str(row["law"]), int(row["year"])
        uri = law_uri(law, year)
        graph.add((uri, RDF.type, BUD.VotedLaw if law == "LF" else BUD.DraftLaw))
        graph.add((uri, BUD.budgetYear, Literal(str(year), datatype=XSD.gYear)))
        graph.add((uri, RDFS.label, Literal(f"{law} {year}")))


def add_institutions(graph: Graph, lines: pd.DataFrame) -> None:
    """One node per budget code, plus its official name in each law."""
    for row in lines.drop_duplicates(["year", "ministry_code"]).to_dict("records"):
        code, name = str(row["ministry_code"]), str(row["ministry_name"])
        institution = institution_uri(code)
        graph.add((institution, RDF.type, BUD.Institution))
        graph.add((institution, BUD.budgetCode, Literal(code)))
        if name.startswith(MINISTRY_PREFIX):
            graph.add((institution, RDF.type, BUD.Ministry))

        official = DATA[f"name/{row['year']}/{code}"]
        label = Literal(name, lang="fr")
        graph.add((official, RDF.type, BUD.OfficialName))
        graph.add((official, BUD.nameOf, institution))
        graph.add((official, BUD.inLaw, law_uri(str(row["law"]), int(row["year"]))))
        graph.add((official, RDFS.label, label))
        graph.add((official, BUD.nameKey, Literal(name_key(name))))


def add_allocations(graph: Graph, lines: pd.DataFrame) -> None:
    for row in lines.to_dict("records"):
        code = str(row["chapter_code"])
        allocation = DATA[f"allocation/{row['year']}/{code}"]
        institution = institution_uri(str(row["ministry_code"]))
        law = law_uri(str(row["law"]), int(row["year"]))
        payment = Literal(int(row["payment_mad"]), datatype=XSD.decimal)
        commitment = Literal(int(row["commitment_mad"]), datatype=XSD.decimal)

        graph.add((allocation, RDF.type, BUD.Allocation))
        graph.add((allocation, BUD.chapterCode, Literal(code)))
        graph.add((allocation, BUD.allocatedTo, institution))
        graph.add((allocation, BUD.inLaw, law))
        graph.add((allocation, BUD.budgetLine, BUD[str(row["budget_line"])]))
        graph.add((allocation, BUD.paymentCredits, payment))
        graph.add((allocation, BUD.commitmentCredits, commitment))


def build_graph() -> Graph:
    lines = pd.read_csv(
        PROCESSED_DIR / "budget_lines.csv", dtype={"ministry_code": str}
    )
    graph = Graph()
    graph.parse(ONTOLOGY_FILE)
    graph.bind("bud", BUD)
    graph.bind("data", DATA)
    add_laws(graph, lines)
    add_institutions(graph, lines)
    add_allocations(graph, lines)
    return graph


def main() -> None:
    graph = build_graph()
    GRAPH_FILE.parent.mkdir(parents=True, exist_ok=True)
    graph.serialize(GRAPH_FILE, format="turtle")
    print(f"{len(graph):,} triples → {GRAPH_FILE.name}")


if __name__ == "__main__":
    main()
