"""RDF namespaces: the ontology (concepts) and the data (facts)."""

from rdflib import Namespace

BASE = "https://github.com/mohamedaminsoumih/morocco-budget-kg/"
BUD = Namespace(BASE + "ontology#")
DATA = Namespace(BASE + "data/")
