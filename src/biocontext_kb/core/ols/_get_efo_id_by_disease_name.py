from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_efo_id_by_disease_name(
    disease_name: Annotated[
        str, Field(description="The name of the disease to search for (e.g., 'choledocholithiasis')")
    ],
    size: Annotated[
        int,
        Field(description="The maximum number of results to return"),
    ] = 5,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform an exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for EFO/Mondo/HP IDs related to a disease name.

    This function searches for EFO IDs associated with a given disease name using the OLS API.
    Always use this function if you need EFO IDs, e.g., for use in the Open Targets API.

    Args:
        disease_name (str): The name of the disease to search for (e.g., "SIDS").
        size (int): Maximum number of results to return (default: 5).
        exact_match (bool): Whether to perform an exact match search (default: False).

    Returns:
        dict: Dictionary containing EFO IDs and information or error message
    """
    if not disease_name:
        return {"error": "disease_name must be provided"}

    url = "https://www.ebi.ac.uk/ols4/api/v2/entities"

    params = {
        "search": disease_name,
        "size": str(size),
        "lang": "en",
        "exactMatch": str(exact_match).lower(),
        "includeObsoleteEntities": "false",
        "ontologyId": "efo",
    }

    def starts_with_valid_prefix(curie: str) -> bool:
        """Check if the curie starts with a valid prefix."""
        return any(curie.startswith(prefix) for prefix in ["EFO:", "MONDO:", "HP:"])

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        # Check that at least one item is in elements and that appearsIn includes EFO
        if not data.get("elements") or not any(
            starts_with_valid_prefix(str(element.get("curie", ""))) for element in data["elements"]
        ):
            return {"error": "No results found"}

        # Extract EFO IDs and their labels
        efo_ids = [
            {
                "id": element["curie"].replace(":", "_"),
                "label": element["label"],
                "description": element.get("description", ""),
            }
            for element in data["elements"]
            if starts_with_valid_prefix(str(element.get("curie", "")))
        ]
        return {"efo_ids": efo_ids}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch EFO IDs: {e!s}"}
