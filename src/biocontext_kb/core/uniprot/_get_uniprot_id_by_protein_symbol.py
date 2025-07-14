from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_uniprot_id_by_protein_symbol(
    protein_symbol: Annotated[str, Field(description="The name of the gene to search for (e.g., 'SYNPO')")],
    species: Annotated[
        str,
        Field(description="The organism ID (e.g., '9606' for human)"),
    ] = "9606",
) -> str | None:
    """Query the UniProt database for the UniProt ID using the protein name.

    Args:
        protein_symbol (str): The name of the protein to search for (e.g., "SYNPO").
        species (str): The organism ID (e.g., "9606" for human). Default is "9606".

    Returns:
        str: The UniProt ID of the protein.

    Raises:
        ValueError: If no results are found for the given protein name.
    """
    url = f"https://rest.uniprot.org/uniprotkb/search?query=protein_name:{protein_symbol}+AND+organism_id:{species}&format=json"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if data["results"]:
        return data["results"][0]["primaryAccession"]

    return None
