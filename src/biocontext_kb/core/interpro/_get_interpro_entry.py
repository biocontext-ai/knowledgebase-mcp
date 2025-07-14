from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_interpro_entry(
    interpro_id: Annotated[
        str,
        Field(description="The InterPro entry identifier (e.g., 'IPR000001')"),
    ],
    include_interactions: Annotated[
        bool,
        Field(description="Whether to include protein-protein interactions data"),
    ] = False,
    include_pathways: Annotated[
        bool,
        Field(description="Whether to include pathway information"),
    ] = False,
    include_cross_references: Annotated[
        bool,
        Field(description="Whether to include cross-references to other databases"),
    ] = False,
) -> dict:
    """Get detailed information about a specific InterPro entry.

    InterPro entries represent protein families, domains, and functional sites.
    Each entry integrates information from multiple member databases.

    Args:
        interpro_id (str): The InterPro entry identifier (e.g., "IPR000001").
        include_interactions (bool, optional): Whether to include protein-protein interactions data. Defaults to False.
        include_pathways (bool, optional): Whether to include pathway information. Defaults to False.
        include_cross_references (bool, optional): Whether to include cross-references to other databases. Defaults to False.

    Returns:
        dict: InterPro entry data including description, type, member databases, and optional additional data
    """
    # Validate InterPro ID format
    interpro_id = interpro_id.upper().strip()
    if not interpro_id.startswith("IPR") or len(interpro_id) != 9:
        return {"error": "Invalid InterPro ID format. Expected format: IPR000001"}

    base_url = f"https://www.ebi.ac.uk/interpro/api/entry/interpro/{interpro_id}"

    # Build query parameters for additional data
    params = {}
    extra_fields = []

    if include_cross_references:
        extra_fields.append("cross_references")

    if extra_fields:
        params["extra_fields"] = ",".join(extra_fields)

    try:
        # Get basic entry information
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        entry_data = response.json()

        if not entry_data.get("metadata"):
            return {"error": f"No data found for InterPro entry {interpro_id}"}

        result = entry_data["metadata"]

        # Optionally fetch interactions data
        if include_interactions:
            try:
                interactions_url = f"{base_url}?interactions"
                interactions_response = requests.get(interactions_url)
                if interactions_response.status_code == 200:
                    interactions_data = interactions_response.json()
                    result["interactions"] = interactions_data.get("results", [])
            except Exception:
                result["interactions"] = {"error": "Could not fetch interactions data"}

        # Optionally fetch pathways data
        if include_pathways:
            try:
                pathways_url = f"{base_url}?pathways"
                pathways_response = requests.get(pathways_url)
                if pathways_response.status_code == 200:
                    pathways_data = pathways_response.json()
                    result["pathways"] = pathways_data.get("results", [])
            except Exception:
                result["pathways"] = {"error": "Could not fetch pathways data"}

        return result

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"InterPro entry {interpro_id} not found"}
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
