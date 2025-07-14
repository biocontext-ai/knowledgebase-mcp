from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_cell_ontology_terms(
    cell_type: Annotated[
        str, Field(description="The cell type to search for (e.g., 'T cell', 'neuron', 'hepatocyte')")
    ],
    size: Annotated[
        int,
        Field(description="The maximum number of results to return"),
    ] = 10,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform an exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for Cell Ontology (CL) terms.

    This function searches for Cell Ontology terms associated with cell types
    using the OLS API. The Cell Ontology provides a controlled vocabulary for cell types.

    Args:
        cell_type (str): The cell type to search for (e.g., "T cell").
        size (int): Maximum number of results to return (default: 10).
        exact_match (bool): Whether to perform an exact match search (default: False).

    Returns:
        dict: Dictionary containing Cell Ontology terms and information or error message
    """
    if not cell_type:
        return {"error": "cell_type must be provided"}

    url = "https://www.ebi.ac.uk/ols4/api/v2/entities"

    params = {
        "search": cell_type,
        "size": str(size),
        "lang": "en",
        "exactMatch": str(exact_match).lower(),
        "includeObsoleteEntities": "false",
        "ontologyId": "cl",
    }

    def starts_with_cl_prefix(curie: str) -> bool:
        """Check if the curie starts with CL prefix."""
        return curie.startswith("CL:")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Check that at least one item is in elements with CL prefix
        if not data.get("elements") or not any(
            starts_with_cl_prefix(str(element.get("curie", ""))) for element in data["elements"]
        ):
            return {"error": "No Cell Ontology terms found"}

        # Extract Cell Ontology terms with detailed information
        cl_terms = [
            {
                "id": element["curie"].replace(":", "_"),
                "label": element.get("label", ""),
                "definition": element.get("definition", ""),
                "synonyms": element.get("synonym", []),
                "ontology_name": element.get("ontologyName", ""),
                "is_defining_ontology": element.get("isDefiningOntology", False),
                "has_hierarchical_children": element.get("hasHierarchicalChildren", False),
                "has_hierarchical_parents": element.get("hasHierarchicalParents", False),
                "num_descendants": element.get("numDescendants", 0),
            }
            for element in data["elements"]
            if starts_with_cl_prefix(str(element.get("curie", "")))
        ]
        return {"cl_terms": cl_terms}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Cell Ontology terms: {e!s}"}
