from typing import Annotated, Any, Dict, Optional, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_studies_by_condition(
    condition: Annotated[str, Field(description="Medical condition/disease (e.g., 'cancer', 'diabetes')")],
    status: Annotated[
        Optional[str],
        Field(description="'RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED', or 'ALL'"),
    ] = "ALL",
    study_type: Annotated[Optional[str], Field(description="'INTERVENTIONAL', 'OBSERVATIONAL', or 'ALL'")] = "ALL",
    location_country: Annotated[Optional[str], Field(description="Country filter (e.g., 'United States')")] = None,
    page_size: Annotated[int, Field(description="Results per page (1-1000)", ge=1, le=1000)] = 50,
    sort: Annotated[
        str,
        Field(description="'LastUpdatePostDate:desc', 'StudyFirstPostDate:desc', or 'EnrollmentCount:desc'"),
    ] = "LastUpdatePostDate:desc",
) -> Union[Dict[str, Any], dict]:
    """Search trials by condition with summary statistics. Returns paginated results with breakdowns by status, study type, and phase.

    Returns:
        dict: Studies list with summary containing condition searched, total studies, status/study type/phase breakdowns or error message.
    """
    if not condition:
        return {"error": "Medical condition must be provided"}

    # Build query components
    query_parts = [f"AREA[ConditionSearch]{condition}"]

    if status and status != "ALL":
        query_parts.append(f"AREA[OverallStatus]{status}")

    if study_type and study_type != "ALL":
        query_parts.append(f"AREA[StudyType]{study_type}")

    if location_country:
        query_parts.append(f"AREA[LocationCountry]{location_country}")

    # Join query parts with AND
    query = " AND ".join(query_parts)

    url = f"https://clinicaltrials.gov/api/v2/studies?query.term={query}&pageSize={page_size}&sort={sort}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Add summary statistics
        if "studies" in data:
            total_studies = data.get("totalCount", len(data["studies"]))

            # Count studies by status
            status_counts: dict[str, int] = {}
            study_type_counts: dict[str, int] = {}
            phase_counts: dict[str, int] = {}

            for study in data["studies"]:
                # Extract status
                status_module = study.get("protocolSection", {}).get("statusModule", {})
                study_status = status_module.get("overallStatus", "Unknown")
                status_counts[study_status] = status_counts.get(study_status, 0) + 1

                # Extract study type
                design_module = study.get("protocolSection", {}).get("designModule", {})
                design_study_type = design_module.get("studyType", "Unknown")
                study_type_counts[design_study_type] = study_type_counts.get(design_study_type, 0) + 1

                # Extract phase for interventional studies
                phases = design_module.get("phases", [])
                if phases:
                    for phase in phases:
                        phase_counts[phase] = phase_counts.get(phase, 0) + 1
                else:
                    phase_counts["N/A"] = phase_counts.get("N/A", 0) + 1

            # Add summary to response
            data["summary"] = {
                "condition_searched": condition,
                "total_studies": total_studies,
                "studies_returned": len(data["studies"]),
                "status_breakdown": status_counts,
                "study_type_breakdown": study_type_counts,
                "phase_breakdown": phase_counts,
            }

        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch studies by condition: {e!s}"}
