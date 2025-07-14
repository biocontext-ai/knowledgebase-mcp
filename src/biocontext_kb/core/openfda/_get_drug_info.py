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
    """Get detailed information about a specific FDA-approved drug by its application number.

    Application numbers follow the format: NDA, ANDA, or BLA followed by 6 digits.
    - NDA: New Drug Application (brand name drugs)
    - ANDA: Abbreviated New Drug Application (generic drugs)
    - BLA: Biologics License Application (biological products)

    Args:
        application_number (str): The FDA application number.

    Returns:
        dict: Detailed drug information from the FDA Drugs@FDA API.
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
    ndc: Annotated[Optional[str], Field(description="National Drug Code (NDC) number")] = None,
) -> dict:
    """Get drug labeling information including active ingredients, dosage, and usage instructions.

    This function retrieves comprehensive drug label information from the FDA's drug labeling
    database, which includes detailed product information, active ingredients, dosage forms,
    and administration routes.

    Args:
        brand_name (str, optional): Brand name of the drug.
        generic_name (str, optional): Generic name of the drug.
        ndc (str, optional): National Drug Code number.

    Returns:
        dict: Drug labeling information from the FDA API.
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
