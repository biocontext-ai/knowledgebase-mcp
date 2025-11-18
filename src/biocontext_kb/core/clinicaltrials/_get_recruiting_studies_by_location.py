from typing import Annotated, Any, Dict, Optional, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_recruiting_studies_by_location(
    location_country: Annotated[str, Field(description="Country name (e.g., 'United States', 'Germany')")],
    location_state: Annotated[Optional[str], Field(description="State/province (e.g., 'California')")] = None,
    location_city: Annotated[Optional[str], Field(description="City name")] = None,
    condition: Annotated[Optional[str], Field(description="Medical condition filter (e.g., 'cancer')")] = None,
    study_type: Annotated[Optional[str], Field(description="'INTERVENTIONAL', 'OBSERVATIONAL', or 'ALL'")] = "ALL",
    age_range: Annotated[Optional[str], Field(description="'CHILD', 'ADULT', 'OLDER_ADULT', or 'ALL'")] = "ALL",
    page_size: Annotated[int, Field(description="Results per page (1-1000)", ge=1, le=1000)] = 50,
) -> Union[Dict[str, Any], dict]:
    """Find recruiting clinical trials by geographic location. Returns paginated results with summary breakdowns.

    Returns:
        dict: Studies list with summary containing search location, total studies, study type/phase/condition breakdowns, recruiting locations or error message.
    """
    if not location_country:
        return {"error": "Location country must be provided"}

    # Build location query using SEARCH operator to ensure geographic coherence
    location_parts = [f"AREA[LocationCountry]{location_country}"]

    if location_state:
        location_parts.append(f"AREA[LocationState]{location_state}")

    if location_city:
        location_parts.append(f"AREA[LocationCity]{location_city}")

    # Combine location parts with SEARCH operator
    location_query = f"SEARCH[Location]({' AND '.join(location_parts)})"

    # Build main query components
    query_parts = [
        "AREA[OverallStatus]RECRUITING",  # Only recruiting studies
        location_query,
    ]

    if condition:
        query_parts.append(f"AREA[ConditionSearch]{condition}")

    if study_type and study_type != "ALL":
        query_parts.append(f"AREA[StudyType]{study_type}")

    if age_range and age_range != "ALL":
        query_parts.append(f"AREA[StdAge]{age_range}")

    # Join query parts with AND
    query = " AND ".join(query_parts)

    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={query}&pageSize={page_size}&sort=LastUpdatePostDate:desc&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Add summary statistics and location analysis
        if "studies" in data:
            total_studies = data.get("totalCount", len(data["studies"]))

            # Analyze locations and conditions
            location_counts: dict[str, int] = {}
            condition_counts: dict[str, int] = {}
            study_type_counts: dict[str, int] = {}
            phase_counts: dict[str, int] = {}

            for study in data["studies"]:
                # Extract study type
                design_module = study.get("protocolSection", {}).get("designModule", {})
                design_study_type = design_module.get("studyType", "Unknown")
                study_type_counts[design_study_type] = study_type_counts.get(design_study_type, 0) + 1

                # Extract phase
                phases = design_module.get("phases", [])
                if phases:
                    for phase in phases:
                        phase_counts[phase] = phase_counts.get(phase, 0) + 1
                else:
                    phase_counts["N/A"] = phase_counts.get("N/A", 0) + 1

                # Extract conditions
                conditions_module = study.get("protocolSection", {}).get("conditionsModule", {})
                conditions = conditions_module.get("conditions", [])
                if conditions:
                    for cond in conditions[:3]:  # Limit to first 3 conditions
                        condition_counts[cond] = condition_counts.get(cond, 0) + 1

                # Extract specific locations
                contacts_module = study.get("protocolSection", {}).get("contactsLocationsModule", {})
                locations = contacts_module.get("locations", [])
                for location in locations:
                    if location.get("status") == "RECRUITING":
                        city = location.get("city", "Unknown")
                        state = location.get("state", "")
                        location_key = f"{city}, {state}" if state else city
                        location_counts[location_key] = location_counts.get(location_key, 0) + 1

            # Add summary to response
            data["summary"] = {
                "search_location": {
                    "country": location_country,
                    "state": location_state,
                    "city": location_city,
                },
                "total_recruiting_studies": total_studies,
                "studies_returned": len(data["studies"]),
                "study_type_breakdown": study_type_counts,
                "phase_breakdown": phase_counts,
                "top_conditions": dict(sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                "recruiting_locations": dict(sorted(location_counts.items(), key=lambda x: x[1], reverse=True)[:15]),
            }

        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch recruiting studies by location: {e!s}"}
