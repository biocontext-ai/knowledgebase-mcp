from typing import Annotated, Any, Dict, Union

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_study_details(
    nct_id: Annotated[str, Field(description="NCT ID (e.g., 'NCT01234567')")],
    fields: Annotated[
        str, Field(description="Comma-separated fields or 'all' for complete data. Default includes key modules.")
    ] = "IdentificationModule,StatusModule,SponsorCollaboratorsModule,DescriptionModule,ConditionsModule,DesignModule,ArmsInterventionsModule,OutcomesModule,EligibilityModule,ContactsLocationsModule",
) -> Union[Dict[str, Any], dict]:
    """Get complete trial details by NCT ID. Retrieves study design, eligibility, outcomes, locations, contacts, and metadata.

    Returns:
        dict: Study details with protocol sections including identification, status, sponsors, description, conditions, design, interventions, outcomes, eligibility, locations or error message.
    """
    if not nct_id:
        return {"error": "NCT ID must be provided"}

    # Validate NCT ID format (should start with NCT followed by 8 digits)
    if not nct_id.upper().startswith("NCT") or len(nct_id) != 11:
        return {"error": "Invalid NCT ID format. Expected format: NCT12345678"}

    # Construct URL
    if fields.lower() == "all":
        url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}?format=json"
    else:
        url = f"https://clinicaltrials.gov/api/v2/studies/{nct_id}?fields={fields}&format=json"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 404:
            return {"error": f"Study with NCT ID '{nct_id}' not found"}
        return {"error": f"Failed to fetch study details: {e!s}"}
