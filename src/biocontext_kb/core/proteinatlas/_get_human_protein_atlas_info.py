from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.ensembl import get_ensembl_id_from_gene_symbol


@core_mcp.tool()
def get_human_protein_atlas_info(
    gene_id: Annotated[Optional[str], Field(description="The Ensembl gene ID (e.g., 'ENSG00000141510')")],
    gene_symbol: Annotated[Optional[str], Field(description="The gene name (e.g., 'TP53')")],
) -> dict:
    """Query the Human Protein Atlas API for target general information, genetic constraint, and tractability."""
    if gene_id is None and gene_symbol is None:
        return {"error": "At least one of gene_id or gene_symbol must be provided"}

    if gene_id is None:
        # If gene_id is not provided, fetch it using gene_symbol
        gene_id_response = get_ensembl_id_from_gene_symbol.fn(gene_symbol=gene_symbol, species="9606")
        if "ensembl_id" in gene_id_response:
            gene_id = gene_id_response["ensembl_id"]
        else:
            return {"error": "Failed to fetch Ensembl ID from gene name"}

    url = f"https://www.proteinatlas.org/{gene_id}.json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Human Protein Atlas info: {e!s}"}
