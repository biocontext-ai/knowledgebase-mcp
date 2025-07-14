from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_grants_gov(
    keyword: Annotated[Optional[str], Field(description="Keyword to search for")] = None,
    opp_num: Annotated[Optional[str], Field(description="Opportunity number")] = None,
    eligibilities: Annotated[Optional[str], Field(description="Eligibility criteria (comma-separated)")] = None,
    agencies: Annotated[Optional[str], Field(description="Agency codes (comma-separated)")] = None,
    rows: Annotated[int, Field(description="Number of results to return")] = 10,
    opp_statuses: Annotated[
        Optional[str], Field(description="Opportunity statuses (pipe-separated, e.g. 'forecasted|posted')")
    ] = "forecasted|posted",
    aln: Annotated[Optional[str], Field(description="Assistance Listing Number")] = None,
    funding_categories: Annotated[Optional[str], Field(description="Funding categories (comma-separated)")] = None,
) -> dict:
    """Search for grants from grants.gov using the Search2 API.

    Args:
        keyword: Keyword to search for
        opp_num: Opportunity number
        eligibilities: Eligibility criteria (comma-separated)
        agencies: Agency codes (comma-separated)
        rows: Number of results to return
        opp_statuses: Opportunity statuses (pipe-separated, e.g. 'forecasted|posted')
        aln: Assistance Listing Number
        funding_categories: Funding categories (comma-separated)

    Returns:
        dict: Search results from grants.gov or error message
    """
    url = "https://api.grants.gov/v1/api/search2"

    # Build request payload
    payload = {"rows": rows, "oppStatuses": opp_statuses or "forecasted|posted"}

    # Add optional parameters if provided
    if keyword:
        payload["keyword"] = keyword
    if opp_num:
        payload["oppNum"] = opp_num
    if eligibilities:
        payload["eligibilities"] = eligibilities
    if agencies:
        payload["agencies"] = agencies
    if aln:
        payload["aln"] = aln
    if funding_categories:
        payload["fundingCategories"] = funding_categories

    try:
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Return the JSON response
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch grants data: {e!s}"}
