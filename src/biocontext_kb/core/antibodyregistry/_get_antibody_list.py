from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_antibody_list(
    search: Annotated[
        str, Field(description="Gene symbol, protein name, or UniProt ID (e.g., 'TRPC6')")
    ],
) -> dict:
    """Search Antibody Registry for antibodies. Returns catalog numbers, vendors, clonality, applications, and metadata.

    Returns:
        dict: Search results containing list of antibodies with catalog numbers, vendors, clonality, applications, metadata or error message.
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
