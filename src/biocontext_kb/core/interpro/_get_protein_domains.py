from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_protein_domains(
    protein_id: Annotated[
        str,
        Field(description="UniProt ID/accession (e.g., 'P04637' or 'CYC_HUMAN')"),
    ],
    source_db: Annotated[
        str,
        Field(description="Database source ('uniprot', 'reviewed', or 'unreviewed')"),
    ] = "uniprot",
    include_structure_info: Annotated[
        bool,
        Field(description="Include structural information"),
    ] = False,
    species_filter: Annotated[
        Optional[str],
        Field(description="Taxonomy ID filter (e.g., '9606' for human)"),
    ] = None,
) -> dict:
    """Get protein domain architecture and InterPro matches. Returns all InterPro domains, functional sites, and domain architecture.

    Returns:
        dict: Protein metadata with interpro_matches array, interpro_match_count, domain_architecture, optionally structure data or error message.
    """
    base_url = f"https://www.ebi.ac.uk/interpro/api/protein/{source_db}/{protein_id}"

    # Build query parameters
    params = {}
    extra_fields = ["description", "sequence"]

    if include_structure_info:
        extra_fields.append("structure")

    if species_filter:
        params["tax_id"] = species_filter

    params["extra_fields"] = ",".join(extra_fields)

    try:
        # Get protein information with InterPro matches
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        protein_data = response.json()

        if not protein_data.get("metadata"):
            return {"error": f"No data found for protein {protein_id}"}

        result = protein_data["metadata"]

        # Get InterPro domain matches for this protein
        try:
            domains_url = f"https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/{source_db}/{protein_id}"
            domains_response = requests.get(domains_url)

            if domains_response.status_code == 200:
                domains_data = domains_response.json()
                result["interpro_matches"] = domains_data.get("results", [])
                result["interpro_match_count"] = len(domains_data.get("results", []))
            else:
                result["interpro_matches"] = []
                result["interpro_match_count"] = 0

        except Exception as e:
            result["interpro_matches"] = {"error": f"Could not fetch InterPro matches: {e}"}

        # Get domain architecture ID (IDA) if available
        try:
            ida_url = f"{base_url}?ida"
            ida_response = requests.get(ida_url)
            if ida_response.status_code == 200:
                ida_data = ida_response.json()
                if ida_data.get("metadata", {}).get("ida"):
                    result["domain_architecture"] = ida_data["metadata"]["ida"]
        except Exception:
            pass  # IDA is optional

        return result

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"Protein {protein_id} not found in {source_db}"}
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
