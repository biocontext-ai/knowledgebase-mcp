from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_drug_by_application_number(
    application_number: Annotated[
        str, Field(description="FDA application number (e.g., 'NDA021436', 'ANDA123456', 'BLA761234')")
    ],
) -> dict:
    """Get detailed information about an FDA-approved drug by application number. Format: NDA/ANDA/BLA followed by 6 digits.

    Returns:
        dict: FDA drug results with application details, products, sponsor information or error message.
    """
    # Validate application number format
    if not application_number or len(application_number) < 9:
        return {"error": "Application number must be provided and follow the format NDA/ANDA/BLA followed by 6 digits"}

    # Build the search query
    query = f"application_number:{application_number}"
    base_url = "https://api.fda.gov/drug/drugsfda.json"
    params = {"search": query, "limit": 1}

    try:
        response = requests.get(base_url, params=params)  # type: ignore
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch FDA drug data: {e!s}"}


@core_mcp.tool()
def get_drug_label_info(
    brand_name: Annotated[Optional[str], Field(description="Brand name of the drug")] = None,
    generic_name: Annotated[Optional[str], Field(description="Generic name of the drug")] = None,
    ndc: Annotated[Optional[str], Field(description="National Drug Code (NDC)")] = None,
) -> dict:
    """Get comprehensive drug labeling information from FDA. Includes active ingredients, dosage forms, administration routes.

    Returns:
        dict: Drug label results with indications, warnings, dosage, active ingredients or error message.
    """
    if not any([brand_name, generic_name, ndc]):
        return {"error": "At least one of brand_name, generic_name, or ndc must be provided"}

    # Use the Drug Label API endpoint
    query_parts = []
    if brand_name:
        query_parts.append(f"openfda.brand_name:{brand_name}")
    if generic_name:
        query_parts.append(f"openfda.generic_name:{generic_name}")
    if ndc:
        query_parts.append(f"openfda.package_ndc:{ndc}")

    query = " OR ".join(query_parts)
    if len(query_parts) > 1:
        query = f"({query})"

    base_url = "https://api.fda.gov/drug/label.json"
    params = {"search": query, "limit": 5}

    try:
        response = requests.get(base_url, params=params)  # type: ignore
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch FDA drug label data: {e!s}"}
