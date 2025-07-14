from typing import Any, Dict

import requests

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_available_ontologies() -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for all available ontologies.

    This function retrieves a list of all ontologies available in OLS, including
    their names, descriptions, and metadata. Use this function first to discover
    which ontologies are available before using other search functions.

    Returns:
        dict: Dictionary containing available ontologies and their information or error message
    """
    url = "https://www.ebi.ac.uk/ols4/api/v2/ontologies"

    params = {
        "size": "300",  # Get a large number of ontologies (as of mid-2025, there are 268)
        "page": "0",
        "lang": "en",
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("elements"):
            return {"error": "No ontologies found"}

        # Extract ontology information
        ontologies = [
            {
                "id": element.get("ontologyId", ""),
                "name": element.get("label", ""),
                "description": element.get("definition", ""),
                "prefix": element.get("ontologyPrefix", ""),
                "base_uri": element.get("baseUri", ""),
                "homepage": element.get("homepage", ""),
                "mailing_list": element.get("mailingList", ""),
                "number_of_terms": element.get("numberOfTerms", 0),
                "number_of_properties": element.get("numberOfProperties", 0),
                "number_of_individuals": element.get("numberOfIndividuals", 0),
                "last_loaded": element.get("lastLoaded", ""),
                "status": element.get("status", ""),
            }
            for element in data["elements"]
        ]

        # Sort by ontology ID for consistency
        ontologies.sort(key=lambda x: x["id"])

        return {
            "ontologies": ontologies,
            "total_ontologies": data.get("totalElements", len(ontologies)),
            "page_info": {
                "page": data.get("page", 0),
                "total_pages": data.get("totalPages", 1),
                "num_elements": data.get("numElements", len(ontologies)),
            },
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch available ontologies: {e!s}"}
