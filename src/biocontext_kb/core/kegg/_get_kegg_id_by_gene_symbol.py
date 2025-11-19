from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.kegg._execute_kegg_query import execute_kegg_query


@core_mcp.tool()
def get_kegg_id_by_gene_symbol(
    gene_symbol: Annotated[str, Field(description="Gene symbol (e.g., 'TP53' for human, 'Trp53' for mouse)")],
    organism_code: Annotated[
        str, Field(description="Taxonomy ID: 9606 (human), 10090 (mouse), 10116 (rat), 562 (E. coli), 4932 (yeast)")
    ],
) -> str | dict:
    """Convert gene symbol to KEGG ID for use in subsequent API calls. Returns KEGG gene ID required for query_kegg().

    Returns:
        str or dict: KEGG gene ID string (e.g., 'hsa:7157') or error dict.
    """
    if not gene_symbol or not organism_code:
        return "Gene symbol and organism code are required."

    organism_name = "human" if organism_code == "9606" else "mouse" if organism_code == "10090" else None
    if organism_name is None:
        return {"error": "Unsupported organism code. Please use 9606 for human or 10090 for mouse."}

    # Get the Entrez ID
    entrez_url = f"https://rest.ensembl.org/xrefs/name/{organism_name}/{gene_symbol}?content-type=application/json&species={organism_code}"
    try:
        response = requests.get(entrez_url)
        response.raise_for_status()
        data = response.json()

        # Filter the data for the first entry where the dbname is "EntrezGene"
        entrez_id = next((item["primary_id"] for item in data if item["dbname"] == "EntrezGene"), None)
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Entrez ID: {e!s}"}
    if not entrez_id:
        return {"error": f"No Entrez ID found for gene symbol: {gene_symbol}"}

    if not gene_symbol or not organism_code:
        return "Gene symbol and organism code are required."

    # Construct the query
    query = f"ncbi-geneid:{entrez_id}"
    path = f"conv/genes/{query}"

    # Execute the query
    try:
        return execute_kegg_query(path)
    except Exception as e:
        return {"error": f"Failed to fetch KEGG ID: {e!s}"}
