from typing import Annotated, Any, Dict, Optional, Union
from urllib.parse import quote

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_studies(
    condition: Annotated[Optional[str], Field(description="Medical condition (e.g., 'cancer')")] = None,
    intervention: Annotated[Optional[str], Field(description="Drug/therapy name (e.g., 'aspirin')")] = None,
    sponsor: Annotated[Optional[str], Field(description="Sponsor org (e.g., 'Pfizer')")] = None,
    status: Annotated[
        Optional[str],
        Field(
            description="'RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED', 'TERMINATED', 'SUSPENDED', 'WITHDRAWN', or 'NOT_YET_RECRUITING'"
        ),
    ] = None,
    phase: Annotated[
        Optional[str], Field(description="'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', 'EARLY_PHASE1', or 'NA'")
    ] = None,
    study_type: Annotated[
        Optional[str], Field(description="'INTERVENTIONAL', 'OBSERVATIONAL', or 'EXPANDED_ACCESS'")
    ] = None,
    location_country: Annotated[Optional[str], Field(description="Country (e.g., 'United States')")] = None,
    min_age: Annotated[Optional[int], Field(description="Min participant age (years)", ge=0)] = None,
    max_age: Annotated[Optional[int], Field(description="Max participant age (years)", ge=0)] = None,
    sex: Annotated[Optional[str], Field(description="'ALL', 'FEMALE', or 'MALE'")] = None,
    page_size: Annotated[int, Field(description="Results per page (1-1000)", ge=1, le=1000)] = 25,
    sort: Annotated[
        str,
        Field(description="'LastUpdatePostDate:desc', 'StudyFirstPostDate:desc', or 'EnrollmentCount:desc'"),
    ] = "LastUpdatePostDate:desc",
) -> Union[Dict[str, Any], dict]:
    """Advanced search for trials with flexible multi-field filtering. Specify at least one search parameter.

    Returns:
        dict: Paginated search results containing studies list with trial metadata or error message.
    """
    # Ensure at least one search parameter was provided
    if not any([condition, intervention, sponsor, status, phase, study_type, location_country, min_age, max_age, sex]):
        return {"error": "At least one search parameter must be provided"}

    # Build query components
    query_parts = []

    if condition:
        query_parts.append(f"AREA[ConditionSearch]{condition}")

    if intervention:
        query_parts.append(f"AREA[InterventionName]{intervention}")

    if sponsor:
        query_parts.append(f"AREA[LeadSponsorName]{sponsor}")

    if status:
        query_parts.append(f"AREA[OverallStatus]{status}")

    if phase:
        query_parts.append(f"AREA[Phase]{phase}")

    if study_type:
        query_parts.append(f"AREA[StudyType]{study_type}")

    if location_country:
        query_parts.append(f"AREA[LocationCountry]{location_country}")

    if sex:
        query_parts.append(f"AREA[Sex]{sex}")

    # Handle age range
    if min_age is not None and max_age is not None:
        query_parts.append(f"AREA[MinimumAge]RANGE[{min_age}, {max_age}]")
    elif min_age is not None:
        query_parts.append(f"AREA[MinimumAge]RANGE[{min_age}, MAX]")
    elif max_age is not None:
        query_parts.append(f"AREA[MaximumAge]RANGE[MIN, {max_age}]")

    # Join query parts with AND
    query = " AND ".join(query_parts)

    # URL encode the query
    encoded_query = quote(query)

    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={encoded_query}&pageSize={page_size}&sort={sort}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch clinical trials: {e!s}"}
