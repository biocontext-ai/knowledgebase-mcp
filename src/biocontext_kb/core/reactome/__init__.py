from typing import Annotated, Any, Dict, List, Optional, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_reactome_info_by_identifier(
    identifier: Annotated[str, Field(description="The identifier of the element to be retrieved")],
    base_url: Annotated[
        str, Field(description="Base URL for the Reactome API")
    ] = "https://reactome.org/AnalysisService",
    interactors: Annotated[bool, Field(description="Include interactors")] = False,
    species: Annotated[
        Optional[Union[str, List[str]]],
        Field(description="List of species to filter the result (accepts taxonomy ids, species names and dbId)"),
    ] = None,
    page_size: Annotated[int, Field(description="Pathways per page", ge=1)] = 20,
    page: Annotated[int, Field(description="Page number", ge=1)] = 1,
    sort_by: Annotated[
        str,
        Field(description="Field to sort results by (e.g., 'ENTITIES_PVALUE', 'ENTITIES_FDR')"),
    ] = "ENTITIES_PVALUE",
    order: Annotated[str, Field(description="Sort order ('ASC' or 'DESC')")] = "ASC",
    resource: Annotated[
        str,
        Field(description="Resource to filter by (TOTAL includes all molecule types)"),
    ] = "TOTAL",
    p_value: Annotated[
        float,
        Field(
            description="P-value threshold (only pathways with p-value <= threshold will be returned)",
            ge=0,
            le=1,
        ),
    ] = 1.0,
    include_disease: Annotated[bool, Field(description="Set to False to exclude disease pathways")] = True,
    min_entities: Annotated[
        Optional[int],
        Field(description="Minimum number of contained entities per pathway"),
    ] = None,
    max_entities: Annotated[
        Optional[int],
        Field(description="Maximum number of contained entities per pathway"),
    ] = None,
    importable_only: Annotated[bool, Field(description="Filter to only include importable resources")] = False,
    timeout: Annotated[int, Field(description="Request timeout in seconds", ge=1)] = 30,
) -> Dict[str, Any]:
    """Query the Reactome API identifier endpoint.

    Use this endpoint to retrieve pathways associated with a given identifier.
    Always provide the species parameter to ensure the correct protein is returned.

    Args:
        identifier (str): The identifier of the element to be retrieved
        base_url (str): Base URL for the Reactome API
        interactors (bool): Include interactors
        species (str or list): List of species to filter the result (accepts taxonomy ids, species names and dbId)
        page_size (int): Pathways per page
        page (int): Page number
        sort_by (str): Field to sort results by (e.g., "ENTITIES_PVALUE", "ENTITIES_FDR")
        order (str): Sort order ("ASC" or "DESC")
        resource (str): Resource to filter by (TOTAL includes all molecule types)
        p_value (float): P-value threshold (only pathways with p-value <= threshold will be returned)
        include_disease (bool): Set to False to exclude disease pathways
        min_entities (int): Minimum number of contained entities per pathway
        max_entities (int): Maximum number of contained entities per pathway
        importable_only (bool): Filter to only include importable resources
        timeout (int): Request timeout in seconds

    Returns:
        dict: API response data or error information
    """
    # Input validation
    if not identifier:
        return {"error": "Identifier cannot be empty"}

    if order not in ["ASC", "DESC"]:
        return {"error": "Order must be either 'ASC' or 'DESC'"}

    if p_value < 0 or p_value > 1:
        return {"error": "P-value must be between 0 and 1"}

    # Build endpoint URL
    endpoint = f"{base_url.rstrip('/')}/identifier/{identifier}"

    # Prepare parameters
    params: dict[str, Union[str, int, float]] = {
        "interactors": str(interactors).lower(),
        "pageSize": page_size,
        "page": page,
        "sortBy": sort_by,
        "order": order,
        "resource": resource,
        "pValue": p_value,
        "includeDisease": str(include_disease).lower(),
        "importableOnly": str(importable_only).lower(),
    }

    # Add optional parameters if provided
    if species:
        if isinstance(species, list):
            params["species"] = ",".join(str(s) for s in species)
        else:
            params["species"] = species

    if min_entities is not None:
        params["min"] = min_entities

    if max_entities is not None:
        params["max"] = max_entities

    try:
        # Make the request
        response = requests.get(endpoint, params=params, timeout=timeout)

        # Return the JSON response if successful
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return {"error": f"Identifier '{identifier}' not found"}
        elif response.status_code == 400:
            return {"error": f"Invalid parameters: {response.text}"}
        else:
            return {
                "error": f"HTTP error occurred: {response.status_code}",
                "details": response.text,
            }

    except requests.exceptions.ConnectionError as conn_err:
        return {"error": f"Connection error: {conn_err!s}"}
    except requests.exceptions.Timeout:
        return {"error": f"Request timed out after {timeout} seconds"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"Request error: {req_err!s}"}
    except Exception as err:
        return {"error": f"Unexpected error: {err!s}"}
