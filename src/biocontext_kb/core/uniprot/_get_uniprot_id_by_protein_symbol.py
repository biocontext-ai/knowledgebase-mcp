from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_uniprot_id_by_protein_symbol(
    protein_symbol: Annotated[str, Field(description="Gene or protein name to search for (e.g., 'SYNPO')")],
    species: Annotated[
        str,
        Field(description="Organism taxonomy ID (e.g., '9606' for human)"),
    ] = "9606",
) -> str | None:
    """Retrieve UniProt accession ID from protein name and species. Returns the primary accession or None if not found.

    Returns:
        str or None: UniProt accession ID string (e.g., 'P04637') or None if not found.
    """
    url = f"https://rest.uniprot.org/uniprotkb/search?query=protein_name:{protein_symbol}+AND+organism_id:{species}&format=json"

    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if data["results"]:
        return data["results"][0]["primaryAccession"]

    return None
