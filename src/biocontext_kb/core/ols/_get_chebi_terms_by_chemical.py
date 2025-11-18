from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_chebi_terms_by_chemical(
    chemical_name: Annotated[
        str, Field(description="Chemical or drug name to search for (e.g., 'aspirin', 'glucose')")
    ],
    size: Annotated[
        int,
        Field(description="Maximum number of results to return"),
    ] = 10,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Search OLS for ChEBI (Chemical Entities of Biological Interest) terms for a chemical or drug name.

    Returns:
        dict: ChEBI terms with chebi_terms array containing id, label, description, synonyms or error message.
    """
    if not chemical_name:
        return {"error": "chemical_name must be provided"}

    url = "https://www.ebi.ac.uk/ols4/api/v2/entities"

    params = {
        "search": chemical_name,
        "size": str(size),
        "lang": "en",
        "exactMatch": str(exact_match).lower(),
        "includeObsoleteEntities": "false",
        "ontologyId": "chebi",
    }

    def starts_with_chebi_prefix(curie: str) -> bool:
        """Check if the curie starts with CHEBI prefix."""
        return curie.startswith("CHEBI:")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Check that at least one item is in elements with CHEBI prefix
        if not data.get("elements") or not any(
            starts_with_chebi_prefix(str(element.get("curie", ""))) for element in data["elements"]
        ):
            return {"error": "No ChEBI terms found"}

        # Extract ChEBI terms and their information
        chebi_terms = [
            {
                "id": element["curie"].replace(":", "_"),
                "label": element["label"],
                "description": element.get("description", ""),
                "ontology_name": element.get("ontologyName", ""),
                "synonyms": element.get("synonyms", []),
            }
            for element in data["elements"]
            if starts_with_chebi_prefix(str(element.get("curie", "")))
        ]
        return {"chebi_terms": chebi_terms}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch ChEBI terms: {e!s}"}
