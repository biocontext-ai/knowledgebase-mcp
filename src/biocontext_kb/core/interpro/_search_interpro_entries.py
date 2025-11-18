from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_interpro_entries(
    query: Annotated[
        Optional[str],
        Field(description="Search term for entry names/descriptions"),
    ] = None,
    entry_type: Annotated[
        Optional[str],
        Field(
            description="family, domain, homologous_superfamily, repeat, conserved_site, binding_site, active_site, or ptm"
        ),
    ] = None,
    source_database: Annotated[
        Optional[str],
        Field(description="pfam, prosite, panther, smart, cdd, hamap, pirsf, prints, etc."),
    ] = None,
    go_term: Annotated[
        Optional[str],
        Field(description="GO term filter (e.g., 'GO:0006122')"),
    ] = None,
    species_filter: Annotated[
        Optional[str],
        Field(description="Taxonomy ID filter (e.g., '9606')"),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Results per page (max 200)"),
    ] = 20,
) -> dict:
    """Search InterPro entries by name, type, database, GO term, or species. Returns matching entries with metadata.

    Returns:
        dict: Search results with results array (InterPro entries), count, total_available, search_criteria or error message.
    """
    base_url = "https://www.ebi.ac.uk/interpro/api/entry/interpro"

    # Build query parameters
    params: dict[str, str | int] = {}

    if page_size > 200:
        page_size = 200
    params["page_size"] = page_size

    # Add the search query if provided (this is the key fix!)
    if query:
        params["search"] = query

    # Add filters
    if entry_type:
        valid_types = [
            "family",
            "domain",
            "homologous_superfamily",
            "repeat",
            "conserved_site",
            "binding_site",
            "active_site",
            "ptm",
        ]
        if entry_type not in valid_types:
            return {"error": f"Invalid entry_type. Valid options: {', '.join(valid_types)}"}
        params["type"] = entry_type

    if source_database:
        valid_dbs = [
            "pfam",
            "prosite",
            "panther",
            "smart",
            "cdd",
            "hamap",
            "pirsf",
            "prints",
            "prodom",
            "ssf",
            "tigrfams",
            "cathgene3d",
            "sfld",
        ]
        if source_database not in valid_dbs:
            return {"error": f"Invalid source_database. Valid options: {', '.join(valid_dbs)}"}
        params["signature_in"] = source_database

    if go_term:
        # Validate GO term format
        if not go_term.upper().startswith("GO:") or len(go_term) != 10:
            return {"error": "Invalid GO term format. Expected format: GO:0006122"}
        params["go_term"] = go_term.upper()

    if species_filter:
        params["tax_id"] = species_filter

    # Add extra fields for more informative results
    params["extra_fields"] = "short_name,description,entry_date"

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        search_results = response.json()

        if not search_results.get("results"):
            return {"results": [], "count": 0, "message": "No InterPro entries found matching the search criteria"}

        # Results are already filtered by the API's search parameter
        results = search_results["results"]

        return {
            "results": results,
            "count": len(results),
            "total_available": search_results.get("count", len(results)),
            "search_criteria": {
                "query": query,
                "entry_type": entry_type,
                "source_database": source_database,
                "go_term": go_term,
                "species_filter": species_filter,
            },
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
