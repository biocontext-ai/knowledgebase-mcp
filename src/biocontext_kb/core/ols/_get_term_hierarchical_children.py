from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_term_hierarchical_children(
    term_id: Annotated[
        str, Field(description="The term ID (CURIE) to get children for (e.g., 'EFO:0000001', 'GO:0008150')")
    ],
    ontology_id: Annotated[
        str, Field(description="The ontology ID where the term is defined (e.g., 'efo', 'go', 'chebi')")
    ],
    size: Annotated[
        int,
        Field(description="The maximum number of children to return"),
    ] = 20,
) -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for hierarchical children of a term.

    This function retrieves the hierarchical children of a specific ontology term,
    including subclasses and terms related via hierarchical properties like 'part of'.

    Args:
        term_id (str): The term ID in CURIE format (e.g., "EFO:0000001").
        ontology_id (str): The ontology ID (e.g., "efo").
        size (int): Maximum number of children to return (default: 20).

    Returns:
        dict: Dictionary containing hierarchical children or error message
    """
    if not term_id:
        return {"error": "term_id must be provided"}
    if not ontology_id:
        return {"error": "ontology_id must be provided"}

    # Double URL encode the term IRI
    import urllib.parse

    term_iri = f"http://purl.obolibrary.org/obo/{term_id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(urllib.parse.quote(term_iri, safe=""), safe="")

    url = f"https://www.ebi.ac.uk/ols4/api/v2/ontologies/{ontology_id}/classes/{encoded_iri}/hierarchicalChildren"

    params = {
        "size": str(size),
        "page": "0",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("elements"):
            return {"error": "No hierarchical children found"}

        # Extract children information
        children = [
            {
                "id": element.get("curie", "").replace(":", "_"),
                "curie": element.get("curie", ""),
                "label": element.get("label", ""),
                "definition": element.get("definition", ""),
                "ontology_name": element.get("ontologyName", ""),
                "has_hierarchical_children": element.get("hasHierarchicalChildren", False),
                "num_descendants": element.get("numDescendants", 0),
            }
            for element in data["elements"]
        ]

        return {
            "parent_term": term_id,
            "hierarchical_children": children,
            "total_children": data.get("totalElements", len(children)),
            "page_info": {
                "page": data.get("page", 0),
                "total_pages": data.get("totalPages", 1),
                "num_elements": data.get("numElements", len(children)),
            },
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch hierarchical children: {e!s}"}
