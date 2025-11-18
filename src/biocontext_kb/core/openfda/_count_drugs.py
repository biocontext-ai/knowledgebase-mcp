from typing import Annotated, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def count_drugs_by_field(
    field: Annotated[
        str,
        Field(
            description="Field to count (e.g., 'sponsor_name', 'products.dosage_form', 'products.route', 'openfda.pharm_class_epc')"
        ),
    ],
    search_filter: Annotated[
        Optional[str], Field(description="Optional search filter to apply before counting")
    ] = None,
    limit: Annotated[int, Field(description="Maximum number of count results to return", ge=1, le=1000)] = 100,
) -> dict:
    """Count unique values in a field across FDA-approved drugs. Useful for statistical analysis.

    Returns:
        dict: Results array with term and count for each unique value or error message.
    """
    # If field is an array, use .exact for correct counting
    array_fields = [
        "openfda.brand_name",
        "openfda.generic_name",
        "openfda.manufacturer_name",
        "openfda.pharm_class_epc",
        "openfda.pharm_class_moa",
        "openfda.pharm_class_pe",
        "openfda.pharm_class_cs",
        "products.brand_name",
    ]
    count_field = field + ".exact" if field in array_fields and not field.endswith(".exact") else field
    url_params = {"count": count_field, "limit": limit}

    # Add search filter if provided
    if search_filter:
        url_params["search"] = search_filter

    # Build the complete URL
    base_url = "https://api.fda.gov/drug/drugsfda.json"

    try:
        response = requests.get(base_url, params=url_params)  # type: ignore
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch FDA drug count data: {e!s}"}


@core_mcp.tool()
def get_drug_statistics() -> dict:
    """Get general statistics about the FDA Drugs@FDA database. Includes top sponsors, dosage forms, routes, marketing status.

    Returns:
        dict: Top sponsors, dosage_forms, administration_routes, marketing_statuses with counts or error message.
    """
    statistics = {}

    try:
        # Get top sponsors
        base_url = "https://api.fda.gov/drug/drugsfda.json"
        sponsors_response = requests.get(base_url, params={"count": "sponsor_name", "limit": 10})  # type: ignore
        sponsors_response.raise_for_status()
        statistics["top_sponsors"] = sponsors_response.json()

        # Get dosage forms
        dosage_response = requests.get(base_url, params={"count": "products.dosage_form", "limit": 15})  # type: ignore
        dosage_response.raise_for_status()
        statistics["dosage_forms"] = dosage_response.json()

        # Get routes of administration
        routes_response = requests.get(base_url, params={"count": "products.route", "limit": 15})  # type: ignore
        routes_response.raise_for_status()
        statistics["administration_routes"] = routes_response.json()

        # Get marketing statuses
        status_response = requests.get(base_url, params={"count": "products.marketing_status", "limit": 10})  # type: ignore
        status_response.raise_for_status()
        statistics["marketing_statuses"] = status_response.json()

        return statistics

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch FDA drug statistics: {e!s}"}
