import re
from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_ensembl_id_from_gene_symbol(
    gene_symbol: Annotated[str, Field(description="The name of the gene to search for (e.g., 'TP53')")],
    species: Annotated[
        str,
        Field(description="Taxonomy ID (e.g., 10090) or species name as string"),
    ] = "9606",
) -> dict:
    """Query the Ensembl database for the Ensembl ID of a given gene name.

    Always provide the species parameter to ensure the correct protein is returned.

    Args:
        gene_symbol (str): The name of the gene to search for (e.g., "TP53").
        species (str): Taxonomy ID (e.g., 10090) as string (default: "9606").

    Returns:
        dict: Gene data or error message
    """
    # Ensure at least one search parameter was provided
    if not gene_symbol:
        return {"error": "gene_symbol must be provided"}

    url = f"https://rest.ensembl.org/xrefs/symbol/{species}/{gene_symbol}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Parse the Ensembl gene ID
        match = re.search(r"\b(ENSG\d+)\b", response.text)

        if match:
            return {"ensembl_id": match.group(1)}
        else:
            return {"error": "No Ensembl gene ID found in response"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Ensembl ID: {e!s}"}
