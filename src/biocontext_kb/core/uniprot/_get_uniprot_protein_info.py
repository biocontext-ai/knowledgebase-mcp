from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_uniprot_protein_info(
    protein_id: Annotated[
        Optional[str],
        Field(description="The protein identifier or accession number (e.g., 'P04637')"),
    ] = None,
    protein_name: Annotated[
        Optional[str],
        Field(description="The name of the protein to search for (e.g., 'P53')"),
    ] = None,
    gene_symbol: Annotated[
        Optional[str],
        Field(description="The gene symbol to search for (e.g., 'TP53')"),
    ] = None,
    species: Annotated[
        Optional[str],
        Field(description="Taxonomy ID (e.g., 10090) or species name as string"),
    ] = None,
    include_references: Annotated[
        bool,
        Field(description="Whether to include references and cross-references in the response"),
    ] = False,
) -> dict:
    """Query the UniProt database for protein information.

    Provide either protein_id or protein_name to search for a specific protein.
    Always provide the species parameter to ensure the correct protein is returned.

    Args:
        protein_id (str, optional): The protein identifier or accession number (e.g., "P04637"). Only provide if protein_name is None.
        protein_name (str, optional): The name of the protein to search for (e.g., "P53").
        gene_symbol (str, optional): The gene name to search for (e.g., "TP53").
        species (str, optional): Taxonomy ID (e.g., 10090) as string.
        include_references (bool, optional): Whether to include references and cross-references in the response. Defaults to False.

    Returns:
        dict: Protein data or error message
    """
    base_url = "https://rest.uniprot.org/uniprotkb/search"

    # Ensure at least one search parameter was provided
    if not protein_id and not protein_name and not gene_symbol:
        return {"error": "At least one of protein_id or protein_name or gene_symbol must be provided."}

    query_parts = []

    if protein_id:
        query_parts.append(f"accession:{protein_id}")

    elif protein_name:
        query_parts.append(f"protein_name:{protein_name}")

    elif gene_symbol:
        query_parts.append(f"gene:{gene_symbol}")

    if species:
        species = str(species).strip()

        # Try to determine if it's a taxonomy ID (numeric) or a name
        if species.isdigit():
            query_parts.append(f"organism_id:{species}")
        else:
            query_parts.append(f'taxonomy_name:"{species}"')

    query = " AND ".join(query_parts)

    params: dict[str, str | int] = {
        "query": query,
        "format": "json",
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        result = response.json()
        if not result.get("results"):
            return {"error": "No results found for the given query."}

        first_result = result["results"][0]

        # Remove references and cross-references by default to reduce response size
        if not include_references:
            first_result.pop("references", None)
            first_result.pop("uniProtKBCrossReferences", None)

        return first_result
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
