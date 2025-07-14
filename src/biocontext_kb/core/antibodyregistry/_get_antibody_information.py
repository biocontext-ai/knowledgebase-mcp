from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_antibody_information(
    ab_id: Annotated[str, Field(description="Antibody ID from the Antibody Registry (e.g., '3643095')")],
) -> dict:
    """Get detailed information for a specific antibody by its ID.

    This function retrieves comprehensive information about a single antibody from the Antibody Registry
    using its unique antibody ID (abId). The antibody ID is typically obtained from the results of
    get_antibody_list() function, where each antibody entry contains an 'abId' field that can be used
    with this function to get detailed information.

    Note: Some information provided by the Antibody Registry is for non-commercial use only.
    Users should refer to antibodyregistry.org for complete terms of use and licensing details.

    Args:
        ab_id (str): The unique antibody ID from the Antibody Registry. This is typically obtained
                    from the 'abId' field in the results of get_antibody_list(), unless the ID
                    is directly provided by the user.

    Returns:
        dict: Detailed antibody information including catalog number, vendor, clonality, epitope,
              applications, target species, isotype, source organism, citations, and other metadata,
              or error message if the request fails.
    """
    ab_id = ab_id.strip()
    if not ab_id:
        return {"error": "Antibody ID cannot be empty."}

    url = f"https://www.antibodyregistry.org/api/antibodies/{ab_id}"

    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list):
            if len(result) > 0:
                # If result is a list, return the first item
                return result[0]
            else:
                return {"error": f"No data found for antibody ID: {ab_id}"}
        elif isinstance(result, dict):
            # If result is a dict, return it directly
            if "abId" in result and result["abId"] == ab_id:
                return result
            else:
                return {"error": f"No data found for antibody ID: {ab_id}"}
        else:
            return {"error": "Unexpected result format from Antibody Registry query."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch antibody information from Antibody Registry: {e!s}"}
