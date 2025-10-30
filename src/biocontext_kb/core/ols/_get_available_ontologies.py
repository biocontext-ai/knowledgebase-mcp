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

    try:
        # First request to get total count
        params = {
            "size": "100",  # OLS now limits to 100 elements per page
            "page": "0",
            "lang": "en",
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("elements"):
            return {"error": "No ontologies found"}

        ontologies: list[Dict[str, Any]] = []
        total_elements = data.get("totalElements", 0)
        total_pages = (total_elements + 99) // 100  # Ceiling division

        # Iterate through all pages
        for page in range(total_pages):
            params["page"] = str(page)
            response = requests.get(url, params=params)
            response.raise_for_status()

            data = response.json()

            # Extract ontology information
            page_ontologies = [
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
                for element in data.get("elements", [])
            ]

            ontologies.extend(page_ontologies)

        # Sort by ontology ID for consistency
        ontologies.sort(key=lambda x: x["id"])

        return {
            "ontologies": ontologies,
            "total_ontologies": total_elements,
            "page_info": {
                "total_pages": total_pages,
                "num_elements": len(ontologies),
            },
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch available ontologies: {e!s}"}
