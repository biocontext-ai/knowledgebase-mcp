from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_drugs_fda(
    brand_name: Annotated[Optional[str], Field(description="Brand or trade name of the drug (e.g., 'Tylenol')")] = None,
    generic_name: Annotated[
        Optional[str], Field(description="Generic name of the drug (e.g., 'acetaminophen')")
    ] = None,
    active_ingredient: Annotated[Optional[str], Field(description="Active ingredient name")] = None,
    sponsor_name: Annotated[Optional[str], Field(description="Company/sponsor name")] = None,
    application_number: Annotated[
        Optional[str], Field(description="FDA application number (NDA, ANDA, or BLA)")
    ] = None,
    marketing_status: Annotated[
        Optional[str],
        Field(
            description="Marketing status: 'Prescription', 'Over-the-counter', 'Discontinued', or 'None (Tentative Approval)'"
        ),
    ] = None,
    dosage_form: Annotated[
        Optional[str], Field(description="Dosage form (e.g., 'TABLET', 'INJECTION', 'CAPSULE')")
    ] = None,
    route: Annotated[
        Optional[str], Field(description="Route of administration (e.g., 'ORAL', 'INJECTION', 'TOPICAL')")
    ] = None,
    search_type: Annotated[
        str, Field(description="Search type: 'and' for all terms must match, 'or' for any term matches")
    ] = "or",
    sort_by: Annotated[
        Optional[str], Field(description="Sort by field (e.g., 'sponsor_name', 'application_number')")
    ] = None,
    limit: Annotated[int, Field(description="Number of results to return", ge=1, le=1000)] = 25,
    skip: Annotated[int, Field(description="Number of results to skip for pagination", ge=0, le=25000)] = 0,
) -> dict:
    """Search the FDA Drugs@FDA database for approved drug products.

    This function searches for FDA-approved drugs based on various criteria including
    brand names, generic names, active ingredients, sponsors, and regulatory information.

    Args:
        brand_name (str, optional): Brand or trade name of the drug.
        generic_name (str, optional): Generic name of the drug.
        active_ingredient (str, optional): Active ingredient name.
        sponsor_name (str, optional): Company or sponsor name.
        application_number (str, optional): FDA application number (NDA, ANDA, or BLA).
        marketing_status (str, optional): Marketing status of the drug.
        dosage_form (str, optional): Dosage form of the drug.
        route (str, optional): Route of administration.
        search_type (str): How to combine search terms - "and" or "or".
        sort_by (str, optional): Field to sort results by.
        limit (int): Maximum number of results to return (1-1000).
        skip (int): Number of results to skip for pagination (0-25000).

    Returns:
        dict: Search results from the FDA Drugs@FDA API.
    """
    # Ensure at least one search parameter is provided
    search_params = [
        brand_name,
        generic_name,
        active_ingredient,
        sponsor_name,
        application_number,
        marketing_status,
        dosage_form,
        route,
    ]
    if not any(search_params):
        return {"error": "At least one search parameter must be provided"}

    # Build query components - using correct schema field paths
    query_parts = []

    if brand_name:
        # Search in both openfda.brand_name and products.brand_name arrays
        query_parts.append(f"(openfda.brand_name:{brand_name} OR products.brand_name:{brand_name})")

    if generic_name:
        # openfda.generic_name is an array
        query_parts.append(f"openfda.generic_name:{generic_name}")

    if active_ingredient:
        # products.active_ingredients.name
        query_parts.append(f"products.active_ingredients.name:{active_ingredient}")

    if sponsor_name:
        query_parts.append(f"sponsor_name:{sponsor_name}")

    if application_number:
        query_parts.append(f"application_number.exact:{application_number}")

    if marketing_status:
        # Map user-friendly terms to API values - products.marketing_status
        status_mapping = {
            "prescription": "1",
            "discontinued": "2",
            "none (tentative approval)": "3",
            "over-the-counter": "4",
        }
        status_value = status_mapping.get(marketing_status.lower(), marketing_status)
        query_parts.append(f"products.marketing_status:{status_value}")

    if dosage_form:
        query_parts.append(f"products.dosage_form:{dosage_form}")

    if route:
        query_parts.append(f"products.route:{route}")

    # Join query parts based on search type
    query = " AND ".join(query_parts) if search_type.lower() == "and" else " OR ".join(query_parts)

    # Build URL parameters for proper encoding
    params = {"search": query, "limit": limit, "skip": skip}

    # Add sorting if specified
    if sort_by:
        params["sort"] = f"{sort_by}:desc"

    # Build the complete URL
    base_url = "https://api.fda.gov/drug/drugsfda.json"

    try:
        response = requests.get(base_url, params=params)  # type: ignore
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch FDA drug data: {e!s}"}
