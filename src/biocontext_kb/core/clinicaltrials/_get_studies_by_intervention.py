from typing import Annotated, Any, Dict, Optional, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_studies_by_intervention(
    intervention: Annotated[
        str,
        Field(description="Drug/therapy name (e.g., 'aspirin', 'pembrolizumab', 'radiation')"),
    ],
    condition: Annotated[Optional[str], Field(description="Medical condition filter (e.g., 'cancer')")] = None,
    phase: Annotated[
        Optional[str], Field(description="'PHASE1', 'PHASE2', 'PHASE3', 'PHASE4', or 'EARLY_PHASE1'")
    ] = None,
    status: Annotated[
        Optional[str], Field(description="'RECRUITING', 'ACTIVE_NOT_RECRUITING', 'COMPLETED', or 'ALL'")
    ] = "ALL",
    intervention_type: Annotated[
        Optional[str],
        Field(description="'DRUG', 'BIOLOGICAL', 'DEVICE', 'PROCEDURE', 'RADIATION', 'BEHAVIORAL', or 'ALL'"),
    ] = "ALL",
    page_size: Annotated[int, Field(description="Results per page (1-1000)", ge=1, le=1000)] = 50,
    sort: Annotated[
        str,
        Field(description="'LastUpdatePostDate:desc', 'StudyFirstPostDate:desc', or 'EnrollmentCount:desc'"),
    ] = "LastUpdatePostDate:desc",
) -> Union[Dict[str, Any], dict]:
    """Search trials by intervention with condition and phase filters. Returns paginated results with breakdowns.

    Returns:
        dict: Studies list with summary containing intervention searched, total studies, status/phase breakdowns, top conditions/sponsors or error message.
    """
    if not intervention:
        return {"error": "Intervention name must be provided"}

    # Build query components
    query_parts = [f"AREA[InterventionName]{intervention}"]

    if condition:
        query_parts.append(f"AREA[ConditionSearch]{condition}")

    if phase:
        query_parts.append(f"AREA[Phase]{phase}")

    if status and status != "ALL":
        query_parts.append(f"AREA[OverallStatus]{status}")

    if intervention_type and intervention_type != "ALL":
        query_parts.append(f"AREA[InterventionType]{intervention_type}")

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

            # Count studies by various attributes
            status_counts: dict[str, int] = {}
            phase_counts: dict[str, int] = {}
            condition_counts: dict[str, int] = {}
            sponsor_counts: dict[str, int] = {}

            for study in data["studies"]:
                # Extract status
                status_module = study.get("protocolSection", {}).get("statusModule", {})
                study_status = status_module.get("overallStatus", "Unknown")
                status_counts[study_status] = status_counts.get(study_status, 0) + 1

                # Extract phase
                design_module = study.get("protocolSection", {}).get("designModule", {})
                phases = design_module.get("phases", [])
                if phases:
                    for phase_item in phases:
                        phase_counts[phase_item] = phase_counts.get(phase_item, 0) + 1
                else:
                    phase_counts["N/A"] = phase_counts.get("N/A", 0) + 1

                # Extract primary conditions
                conditions_module = study.get("protocolSection", {}).get("conditionsModule", {})
                conditions = conditions_module.get("conditions", [])
                if conditions:
                    for cond in conditions[:3]:  # Limit to first 3 conditions
                        condition_counts[cond] = condition_counts.get(cond, 0) + 1

                # Extract lead sponsor
                sponsor_module = study.get("protocolSection", {}).get("sponsorCollaboratorsModule", {})
                lead_sponsor = sponsor_module.get("leadSponsor", {}).get("name", "Unknown")
                sponsor_counts[lead_sponsor] = sponsor_counts.get(lead_sponsor, 0) + 1

            # Add summary to response
            data["summary"] = {
                "intervention_searched": intervention,
                "total_studies": total_studies,
                "studies_returned": len(data["studies"]),
                "status_breakdown": status_counts,
                "phase_breakdown": phase_counts,
                "top_conditions": dict(sorted(condition_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
                "top_sponsors": dict(sorted(sponsor_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            }

        return data
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch studies by intervention: {e!s}"}
