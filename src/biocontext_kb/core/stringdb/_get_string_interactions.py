from typing import Annotated, Any, Dict, List, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.stringdb._get_string_id import get_string_id


@core_mcp.tool()
def get_string_interactions(
    protein_symbol: Annotated[str, Field(description="Protein name to search for (e.g., 'TP53')")],
    species: Annotated[str, Field(description="Species taxonomy ID (e.g., '10090' for mouse)")],
    min_score: Annotated[int, Field(description="Minimum combined score threshold (0-1000)", ge=0, le=1000)] = 700,
) -> Union[List[Dict[str, Any]], dict]:
    """Retrieve protein-protein interactions for a given protein with scores above threshold. Always provide species parameter.

    Returns:
        list or dict: Protein interactions array with stringId_A, stringId_B, preferredName_A/B, score, evidence channels or error message.
    """
    # First resolve the protein name to a STRING ID
    try:
        string_id = get_string_id.fn(protein_symbol=protein_symbol, species=species)

        if not string_id or not isinstance(string_id, str):
            return {"error": f"No STRING ID found for protein: {protein_symbol}"}

        url = f"https://string-db.org/api/json/interaction_partners?identifiers={string_id}&species={species}&required_score={min_score}&format=json"
        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch interactions: {e!s}"}
    except Exception as e:
        return {"error": f"An error occurred: {e!s}"}
