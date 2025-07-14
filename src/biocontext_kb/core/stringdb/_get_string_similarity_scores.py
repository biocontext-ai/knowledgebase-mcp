from typing import Annotated, Any, Dict, List, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.stringdb._get_string_id import get_string_id


@core_mcp.tool()
def get_string_similarity_scores(
    protein_symbol: Annotated[str, Field(description="The protein symbol of the first protein (e.g., 'TP53')")],
    protein_symbol_comparison: Annotated[
        str, Field(description="The protein symbol of the second protein (e.g., 'MKI67')")
    ],
    species: Annotated[str, Field(description="The species taxonomy ID (e.g., '9606' for human)")] = "",
) -> Union[List[Dict[str, Any]], dict]:
    """Get similarity scores between proteins from the STRING database.

    The scores represent protein homology based on Smith-Waterman bit scores.
    Only scores above 50 are reported, and only half of the similarity matrix
    (since it's symmetric) plus self-hits are returned.

    Args:
        protein_symbol (str): The protein symbol of the first protein (e.g., "TP53").
        protein_symbol_comparison (str): The protein symbol of the second protein (e.g., "MKI67").
        species (str): The species taxonomy ID (e.g., "9606" for human). Optional.

    Returns:
        list: A list of dictionaries containing protein pairs and their bit scores.
    """
    # Resolve both protein symbols to STRING IDs
    try:
        string_id1 = get_string_id.fn(protein_symbol=protein_symbol, species=species)
        string_id2 = get_string_id.fn(protein_symbol=protein_symbol_comparison, species=species)

        if not all(isinstance(string_id, str) for string_id in [string_id1, string_id2]):
            return {"error": "Could not extract STRING IDs"}

        identifiers = f"{string_id1}%0d{string_id2}"

        url = f"https://string-db.org/api/json/homology?identifiers={identifiers}"
        if species:
            url += f"&species={species}"

        response = requests.get(url)
        response.raise_for_status()

        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch similarity scores: {e!s}"}
    except Exception as e:
        return {"error": f"An error occurred: {e!s}"}
