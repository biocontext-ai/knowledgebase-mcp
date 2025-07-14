from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_antibody_list(
    search: Annotated[
        str, Field(description="Search term for antibodies (e.g., gene symbol, protein name, UniProt ID)")
    ],
) -> dict:
    """Query the Antibody Registry for available antibodies.

    This function searches the Antibody Registry database for antibodies matching the search term.
    Common search parameters include gene symbols (e.g., 'TRPC6'), protein names, UniProt IDs,
    or other relevant identifiers.

    Note: Some information provided by the Antibody Registry is for non-commercial use only.
    Users should refer to antibodyregistry.org for complete terms of use and licensing details.

    Args:
        search (str): Search term for antibodies. Can be a gene symbol, protein name, UniProt ID, or similar identifier.

    Returns:
        dict: Antibody search results including catalog numbers, vendor information, clonality,
              applications, and other antibody metadata, or error message if the request fails.
    """
    search = search.strip()
    if not search:
        return {"error": "Search term cannot be empty."}

    url = "https://www.antibodyregistry.org/api/antibodies/search"

    params = {"search": search}

    headers = {"accept": "application/json"}

    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch antibody information from Antibody Registry: {e!s}"}
