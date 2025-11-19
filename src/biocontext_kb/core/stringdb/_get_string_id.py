from typing import Annotated, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_string_id(
    protein_symbol: Annotated[str, Field(description="Protein name or identifier (e.g., 'TP53')")],
    species: Annotated[str, Field(description="Species taxonomy ID (e.g., '9606' for human)")] = "",
    return_field: Annotated[str, Field(description="Field to return: 'stringId' or 'preferredName'")] = "stringId",
    limit: Annotated[int, Field(description="Maximum number of matches to return")] = 1,
) -> Union[dict, str]:
    """Map protein identifiers (gene names, synonyms, UniProt IDs) to STRING database IDs. Using STRING IDs improves reliability.

    Returns:
        str or dict: STRING ID string (e.g., '9606.ENSP00000269305') or dict with error message.
    """
    url = f"https://string-db.org/api/json/get_string_ids?identifiers={protein_symbol}&echo_query=1&limit={limit}"

    if species:
        url += f"&species={species}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if isinstance(data, dict) and "error" in data:
            return data

        if not data:
            return {"error": f"No STRING ID found for protein: {protein_symbol}"}

        return data[0].get(return_field)
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch STRING ID: {e!s}"}
