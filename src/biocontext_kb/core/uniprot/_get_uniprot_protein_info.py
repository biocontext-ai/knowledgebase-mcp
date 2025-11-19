from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_uniprot_protein_info(
    protein_id: Annotated[
        Optional[str],
        Field(description="Protein accession number (e.g., 'P04637')"),
    ] = None,
    protein_name: Annotated[
        Optional[str],
        Field(description="Protein name to search for (e.g., 'P53')"),
    ] = None,
    gene_symbol: Annotated[
        Optional[str],
        Field(description="Gene symbol to search for (e.g., 'TP53')"),
    ] = None,
    species: Annotated[
        Optional[str],
        Field(description="Taxonomy ID (e.g., '10090') or species name"),
    ] = None,
    include_references: Annotated[
        bool,
        Field(description="Include references and cross-references in response"),
    ] = False,
) -> dict:
    """Retrieve protein information from UniProt database. Provide at least one of protein_id, protein_name, or gene_symbol.

    Returns:
        dict: Protein information with accession, proteinDescription, genes, organism, sequence, functions, keywords, references or error message.
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
