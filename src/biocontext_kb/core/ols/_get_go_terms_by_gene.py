from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_go_terms_by_gene(
    gene_name: Annotated[str, Field(description="The gene name or symbol to search for (e.g., 'TP53', 'BRCA1')")],
    size: Annotated[
        int,
        Field(description="The maximum number of results to return"),
    ] = 10,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform an exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for Gene Ontology (GO) terms related to a gene name.

    This function searches for GO terms associated with a given gene name using the OLS API.
    Gene Ontology provides structured vocabularies for gene and gene product attributes.

    Args:
        gene_name (str): The gene name or symbol to search for (e.g., "TP53").
        size (int): Maximum number of results to return (default: 10).
        exact_match (bool): Whether to perform an exact match search (default: False).

    Returns:
        dict: Dictionary containing GO terms and information or error message
    """
    if not gene_name:
        return {"error": "gene_name must be provided"}

    url = "https://www.ebi.ac.uk/ols4/api/v2/entities"

    params = {
        "search": gene_name,
        "size": str(size),
        "lang": "en",
        "exactMatch": str(exact_match).lower(),
        "includeObsoleteEntities": "false",
        "ontologyId": "go",
    }

    def starts_with_go_prefix(curie: str) -> bool:
        """Check if the curie starts with GO prefix."""
        return curie.startswith("GO:")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Check that at least one item is in elements with GO prefix
        if not data.get("elements") or not any(
            starts_with_go_prefix(str(element.get("curie", ""))) for element in data["elements"]
        ):
            return {"error": "No GO terms found"}

        # Extract GO terms and their information
        go_terms = [
            {
                "id": element["curie"].replace(":", "_"),
                "label": element["label"],
                "description": element.get("description", ""),
                "ontology_name": element.get("ontologyName", ""),
                "type": element.get("type", ""),
            }
            for element in data["elements"]
            if starts_with_go_prefix(str(element.get("curie", "")))
        ]
        return {"go_terms": go_terms}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch GO terms: {e!s}"}
