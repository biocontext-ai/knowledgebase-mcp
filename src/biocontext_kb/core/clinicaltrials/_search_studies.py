from typing import Annotated, Any, Dict, Optional, Union
from urllib.parse import quote

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_studies(
    condition: Annotated[
        Optional[str], Field(description="Medical condition or disease (e.g., 'cancer', 'diabetes')")
    ] = None,
    intervention: Annotated[
        Optional[str], Field(description="Drug, therapy, or treatment name (e.g., 'aspirin', 'chemotherapy')")
    ] = None,
    sponsor: Annotated[Optional[str], Field(description="Study sponsor organization (e.g., 'Pfizer', 'NIH')")] = None,
    status: Annotated[
        Optional[str],
        Field(
            description="Study status: 'RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED', 'TERMINATED', 'SUSPENDED', 'WITHDRAWN', 'NOT_YET_RECRUITING'"
        ),
    ] = None,
    phase: Annotated[
        Optional[str], Field(description="Study phase: 'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', 'EARLY_PHASE1', 'NA'")
    ] = None,
    study_type: Annotated[
        Optional[str], Field(description="Type of study: 'INTERVENTIONAL', 'OBSERVATIONAL', 'EXPANDED_ACCESS'")
    ] = None,
    location_country: Annotated[
        Optional[str], Field(description="Country where study is conducted (e.g., 'United States', 'Germany')")
    ] = None,
    min_age: Annotated[Optional[int], Field(description="Minimum age of participants in years", ge=0)] = None,
    max_age: Annotated[Optional[int], Field(description="Maximum age of participants in years", ge=0)] = None,
    sex: Annotated[Optional[str], Field(description="Sex of participants: 'ALL', 'FEMALE', 'MALE'")] = None,
    page_size: Annotated[int, Field(description="Number of results to return", ge=1, le=1000)] = 25,
    sort: Annotated[
        str,
        Field(description="Sort order: 'LastUpdatePostDate:desc', 'StudyFirstPostDate:desc', 'EnrollmentCount:desc'"),
    ] = "LastUpdatePostDate:desc",
) -> Union[Dict[str, Any], dict]:
    """Search for clinical trials studies based on various criteria.

    This function allows biomedical researchers to find relevant clinical trials by searching
    across conditions, interventions, sponsors, and other study characteristics.

    Args:
        condition (str, optional): Medical condition or disease to search for.
        intervention (str, optional): Drug, therapy, or treatment name to search for.
        sponsor (str, optional): Study sponsor organization.
        status (str, optional): Current status of the study.
        phase (str, optional): Clinical trial phase.
        study_type (str, optional): Type of study (interventional, observational, etc.).
        location_country (str, optional): Country where study is conducted.
        min_age (int, optional): Minimum age of participants in years.
        max_age (int, optional): Maximum age of participants in years.
        sex (str, optional): Sex of participants.
        page_size (int): Number of results to return (default: 25, max: 1000).
        sort (str): Sort order for results (default: most recently updated).

    Returns:
        dict: Study search results or error message
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
