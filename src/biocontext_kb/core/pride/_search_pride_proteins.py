from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_pride_proteins(
    project_accession: Annotated[
        str,
        Field(description="The PRIDE project accession to search proteins in"),
    ],
    keyword: Annotated[
        Optional[str],
        Field(description="Search keyword for protein names or accessions"),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Number of results to return (max 100)"),
    ] = 20,
    sort_field: Annotated[
        str,
        Field(description="Field to sort by: accession, proteinName, gene"),
    ] = "accession",
    sort_direction: Annotated[
        str,
        Field(description="Sort direction: ASC or DESC"),
    ] = "ASC",
) -> dict:
    """Search proteins identified in a specific PRIDE project.

    This function searches for proteins identified in a specific PRIDE mass
    spectrometry project. Useful for finding specific proteins of interest
    in proteomics datasets.

    Args:
        project_accession (str): The PRIDE project accession to search in.
        keyword (str, optional): Search keyword for protein names or accessions.
        page_size (int, optional): Number of results (max 100). Defaults to 20.
        sort_field (str, optional): Sort field. Defaults to "accession".
        sort_direction (str, optional): Sort direction. Defaults to "ASC".

    Returns:
        dict: Search results with proteins found in the specified project
    """
    base_url = "https://www.ebi.ac.uk/pride/ws/archive/v3/pride-ap/search/proteins"

    # Build query parameters
    params: dict[str, str | int] = {"projectAccession": project_accession}

    if page_size > 100:
        page_size = 100
    params["pageSize"] = page_size
    params["page"] = 0

    # Add keyword search
    if keyword:
        params["keyword"] = keyword

    # Validate and set sort parameters
    valid_sort_fields = ["accession", "proteinName", "gene"]
    if sort_field not in valid_sort_fields:
        sort_field = "accession"
    params["sortField"] = sort_field

    valid_sort_directions = ["ASC", "DESC"]
    if sort_direction.upper() not in valid_sort_directions:
        sort_direction = "ASC"
    params["sortDirection"] = sort_direction.upper()

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        search_results = response.json()

        if not search_results:
            return {"results": [], "count": 0, "message": f"No proteins found in PRIDE project {project_accession}"}

        # Process results to include key information
        processed_results = []
        for protein in search_results:
            processed_protein = {
                "protein_accession": protein.get("proteinAccession"),
                "protein_name": protein.get("proteinName"),
                "gene": protein.get("gene"),
                "project_count": protein.get("projectCount", 0),
            }
            processed_results.append(processed_protein)

        return {
            "results": processed_results,
            "count": len(processed_results),
            "project_accession": project_accession,
            "search_criteria": {"keyword": keyword, "sort_field": sort_field, "sort_direction": sort_direction},
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"PRIDE project {project_accession} not found or has no protein data"}
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
