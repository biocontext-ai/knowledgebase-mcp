from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_pride_projects(
    keyword: Annotated[
        Optional[str],
        Field(description="Search keywords (e.g., 'proteome', 'cancer', 'human')"),
    ] = None,
    organism_filter: Annotated[
        Optional[str],
        Field(description="Filter by organism (e.g., 'Homo sapiens', 'human')"),
    ] = None,
    instrument_filter: Annotated[
        Optional[str],
        Field(description="Filter by instrument type (e.g., 'Orbitrap', 'LTQ')"),
    ] = None,
    experiment_type_filter: Annotated[
        Optional[str],
        Field(description="Filter by experiment type (e.g., 'TMT', 'Label-free')"),
    ] = None,
    page_size: Annotated[
        int,
        Field(description="Number of results to return (max 100)"),
    ] = 20,
    sort_field: Annotated[
        str,
        Field(description="Field to sort by: submissionDate, publicationDate"),
    ] = "submissionDate",
    sort_direction: Annotated[
        str,
        Field(description="Sort direction: ASC or DESC"),
    ] = "DESC",
) -> dict:
    """Search PRIDE Archive projects by various criteria.

    This function searches the PRIDE database for mass spectrometry proteomics
    projects using keywords and filters. Useful for finding relevant datasets
    for comparative analysis or method validation.

    Args:
        keyword (str, optional): Search keywords for project titles/descriptions.
        organism_filter (str, optional): Filter by organism name.
        instrument_filter (str, optional): Filter by mass spectrometer instrument.
        experiment_type_filter (str, optional): Filter by experimental approach.
        page_size (int, optional): Number of results (max 100). Defaults to 20.
        sort_field (str, optional): Sort field. Defaults to "submissionDate".
        sort_direction (str, optional): Sort direction. Defaults to "DESC".

    Returns:
        dict: Search results with matching PRIDE projects and metadata
    """
    base_url = "https://www.ebi.ac.uk/pride/ws/archive/v3/search/projects"

    # Build query parameters
    params: dict[str, str | int] = {}

    if page_size > 100:
        page_size = 100
    params["pageSize"] = page_size
    params["page"] = 0

    # Add keyword search
    if keyword:
        params["keyword"] = keyword

    # Build filter string for specific criteria
    filters = []
    if organism_filter:
        filters.append(f"organisms=={organism_filter}")
    if instrument_filter:
        filters.append(f"instruments=={instrument_filter}")
    if experiment_type_filter:
        filters.append(f"experimentTypes=={experiment_type_filter}")

    if filters:
        params["filter"] = ",".join(filters)

    # Validate and set sort parameters - use only known working fields
    valid_sort_fields = ["submissionDate", "publicationDate"]
    if sort_field not in valid_sort_fields:
        sort_field = "submissionDate"
    params["sortFields"] = sort_field

    valid_sort_directions = ["ASC", "DESC"]
    if sort_direction.upper() not in valid_sort_directions:
        sort_direction = "DESC"
    params["sortDirection"] = sort_direction.upper()

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()

        search_results = response.json()

        if not search_results:
            return {
                "results": [],
                "count": 0,
                "message": "No PRIDE projects found matching the search criteria",
                "search_criteria": {
                    "keyword": keyword,
                    "organism_filter": organism_filter,
                    "instrument_filter": instrument_filter,
                    "experiment_type_filter": experiment_type_filter,
                    "sort_field": sort_field,
                    "sort_direction": sort_direction,
                },
            }

        # Process results to include key information
        processed_results = []
        for project in search_results:
            processed_project = {
                "accession": project.get("accession"),
                "title": project.get("title"),
                "description": project.get("projectDescription", "")[:500] + "..."
                if len(project.get("projectDescription", "")) > 500
                else project.get("projectDescription", ""),
                "submission_date": project.get("submissionDate"),
                "publication_date": project.get("publicationDate"),
                "organisms": project.get("organisms", []),
                "instruments": project.get("instruments", []),
                "experiment_types": project.get("experimentTypes", []),
                "keywords": project.get("keywords", []),
                "submitters": project.get("submitters", []),
                "download_count": project.get("downloadCount", 0),
            }
            processed_results.append(processed_project)

        return {
            "results": processed_results,
            "count": len(processed_results),
            "search_criteria": {
                "keyword": keyword,
                "organism_filter": organism_filter,
                "instrument_filter": instrument_filter,
                "experiment_type_filter": experiment_type_filter,
                "sort_field": sort_field,
                "sort_direction": sort_direction,
            },
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
