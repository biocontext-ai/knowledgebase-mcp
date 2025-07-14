from typing import Annotated, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_string_id(
    protein_symbol: Annotated[str, Field(description="The name of the protein to search for (e.g., 'TP53')")],
    species: Annotated[str, Field(description="The species taxonomy ID (e.g., '9606' for human)")] = "",
    return_field: Annotated[
        str, Field(description="Which field to return. Either `stringId` (default) or `preferredName`.")
    ] = "stringId",
    limit: Annotated[int, Field(description="Limit the number of matches returned")] = 1,
) -> Union[dict, str]:
    """Map a protein identifier to STRING database IDs.

    This function helps resolve common gene names, synonyms, or UniProt identifiers
    to the STRING-specific identifiers. Using STRING IDs in subsequent API calls
    improves reliability and performance.

    Args:
        protein_symbol (str): The name of the protein to search for (e.g., "TP53").
        species (str): The species taxonomy ID (e.g., "9606" for human). Optional.
        return_field (str): The field to return. Either `stringId` or `preferredName` (default: stringId).
        limit (int): Limit the number of matches returned per query (default: 1).

    Returns:
        str: The STRING ID or preferred name if found, otherwise an error message.
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
