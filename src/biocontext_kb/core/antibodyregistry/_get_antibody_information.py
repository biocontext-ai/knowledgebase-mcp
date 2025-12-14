from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_antibody_information(
    ab_id: Annotated[str, Field(description="Antibody Registry ID (e.g., '3643095')")],
) -> dict:
    """Get detailed antibody information by ID. Retrieves catalog number, vendor, clonality, epitope, applications, and more.

    Returns:
        dict: Antibody details including abId, catalog numbers, vendor, clonality, epitope, applications, target species, isotype, citations or error message.
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

        # API returns an array of antibodies
        if isinstance(result, list):
            if len(result) > 0:
                # Return the first item from the array
                return result[0]
            else:
                return {"error": f"No data found for antibody ID: {ab_id}"}
        else:
            return {"error": "Unexpected result format from Antibody Registry query."}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch antibody information from Antibody Registry: {e!s}"}
