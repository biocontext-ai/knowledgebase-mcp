from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.alphafold._get_alphafold_info_by_uniprot_id import (
    get_alphafold_info_by_uniprot_id,
)
from biocontext_kb.core.uniprot._get_uniprot_id_by_protein_symbol import (
    get_uniprot_id_by_protein_symbol,
)


@core_mcp.tool()
def get_alphafold_info_by_protein_symbol(
    protein_symbol: Annotated[str, Field(description="Gene/protein name (e.g., 'SYNPO')")],
    species: Annotated[
        str,
        Field(description="Taxonomy ID (e.g., '9606' for human)"),
    ] = "9606",
) -> dict:
    """Query AlphaFold database using protein name. First converts protein symbol to UniProt ID, then fetches structure predictions.

    Returns:
        dict: AlphaFold prediction data including PDB/CIF file URLs, confidence scores, and metadata or error message.
    """
    # Get the UniProt Id from the protein_symbol
    try:
        uniprot_id = get_uniprot_id_by_protein_symbol.fn(protein_symbol, species)

        if uniprot_id:
            result = get_alphafold_info_by_uniprot_id(uniprot_id)
            if isinstance(result, dict) and "error" in result:
                return {"error": result["error"]}
            elif isinstance(result, list) and len(result) > 0:
                # If result is a list, return the first item
                return result[0]
            elif isinstance(result, dict):
                # If result is a dict, return it directly
                return result
            else:
                return {"error": "Unexpected result format from AlphaFold query"}
        else:
            return {"error": "No results found for the given protein name"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch AlphaFold info: {e!s}"}
