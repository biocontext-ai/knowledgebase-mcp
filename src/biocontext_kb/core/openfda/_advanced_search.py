from typing import Annotated, Any

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_available_pharmacologic_classes(
    class_type: Annotated[
        str,
        Field(
            description="Type of pharmacologic class: 'epc' (Established Pharmacologic Class), 'moa' (Mechanism of Action), 'pe' (Physiologic Effect), or 'cs' (Chemical Structure)"
        ),
    ] = "epc",
    limit: Annotated[int, Field(description="Number of unique classes to return", ge=1, le=1000)] = 100,
) -> dict:
    """Get available pharmacologic classes from the FDA database.

    This function retrieves the actual pharmacologic class values available in the
    FDA database, which can then be used with search_drugs_by_therapeutic_class.
    Always call this function first to see available options before searching.

    Args:
        class_type (str): Type of classification - epc, moa, pe, or cs.
        limit (int): Maximum number of unique classes to return.

    Returns:
        dict: Available pharmacologic class values in the FDA database.
    """
    # Map class type to the appropriate OpenFDA field
    class_field_mapping = {
        "epc": "openfda.pharm_class_epc",  # Established Pharmacologic Class
        "moa": "openfda.pharm_class_moa",  # Mechanism of Action
        "pe": "openfda.pharm_class_pe",  # Physiologic Effect
        "cs": "openfda.pharm_class_cs",  # Chemical Structure
    }

    if class_type.lower() not in class_field_mapping:
        return {"error": "class_type must be one of: epc, moa, pe, cs"}

    field = class_field_mapping[class_type.lower()]

    # Use the count endpoint to get unique values
    base_url = "https://api.fda.gov/drug/drugsfda.json"
    params: Any = {"count": field, "limit": limit}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "class_type": class_type,
            "field": field,
            "available_classes": data.get("results", []),
            "total_found": len(data.get("results", [])),
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch available pharmacologic classes: {e!s}"}


@core_mcp.tool()
def search_drugs_by_therapeutic_class(
    therapeutic_class: Annotated[
        str,
        Field(
            description="Exact therapeutic/pharmacologic class term from FDA database (use get_available_pharmacologic_classes first to see options)"
        ),
    ],
    class_type: Annotated[
        str,
        Field(
            description="Type of pharmacologic class: 'epc' (Established Pharmacologic Class), 'moa' (Mechanism of Action), 'pe' (Physiologic Effect), or 'cs' (Chemical Structure)"
        ),
    ] = "epc",
    limit: Annotated[int, Field(description="Number of results to return", ge=1, le=1000)] = 25,
) -> dict:
    """Search for drugs by their therapeutic or pharmacologic class.

    IMPORTANT: Use get_available_pharmacologic_classes() first to see the exact
    class terms available in the FDA database. This function requires exact matches
    of the pharmacologic class terms as they appear in the FDA data.

    Args:
        therapeutic_class (str): The exact therapeutic class term from FDA database.
        class_type (str): Type of classification - epc, moa, pe, or cs.
        limit (int): Maximum number of results to return.

    Returns:
        dict: Search results for drugs in the specified therapeutic class.
    """
    # Map class type to the appropriate OpenFDA field
    class_field_mapping = {
        "epc": "openfda.pharm_class_epc",  # Established Pharmacologic Class
        "moa": "openfda.pharm_class_moa",  # Mechanism of Action
        "pe": "openfda.pharm_class_pe",  # Physiologic Effect
        "cs": "openfda.pharm_class_cs",  # Chemical Structure
    }

    if class_type.lower() not in class_field_mapping:
        return {"error": "class_type must be one of: epc, moa, pe, cs"}

    field = class_field_mapping[class_type.lower()]

    # Use exact term as provided - no mapping since user should get this from get_available_pharmacologic_classes
    query = f'{field}:"{therapeutic_class}"'

    base_url = "https://api.fda.gov/drug/drugsfda.json"
    params: Any = {"search": query, "limit": limit}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch drugs by therapeutic class: {e!s}"}


@core_mcp.tool()
def get_generic_equivalents(
    brand_name: Annotated[str, Field(description="Brand name drug to find generic equivalents for")],
) -> dict:
    """Find generic equivalents for a brand name drug.

    This function searches for ANDA (Abbreviated New Drug Application) entries
    that are generic equivalents of a specified brand name drug.

    Args:
        brand_name (str): The brand name drug to find generics for.

    Returns:
        dict: Generic drug equivalents and their manufacturers.
    """
    # First, search for the brand name drug to get its active ingredient
    brand_query = f"(openfda.brand_name:{brand_name} OR products.brand_name:{brand_name})"
    base_url = "https://api.fda.gov/drug/drugsfda.json"
    brand_params: Any = {"search": brand_query, "limit": 1}

    try:
        brand_response = requests.get(base_url, params=brand_params)
        brand_response.raise_for_status()
        brand_data = brand_response.json()

        if not brand_data.get("results"):
            return {"error": f"Brand name drug '{brand_name}' not found in FDA database"}

        # Extract active ingredients from the brand drug
        brand_drug = brand_data["results"][0]

        # Check if we have products and active ingredients
        if not brand_drug.get("products"):
            return {"error": f"Could not find product information for '{brand_name}'"}

        # Search for generic drugs (ANDA applications) with similar active ingredients
        generic_results = []

        # Try to find active ingredients from the first product
        for product in brand_drug["products"][:1]:  # Just check first product
            if product.get("active_ingredients"):
                active_ingredients = product["active_ingredients"]

                # Handle case where active_ingredients might be an object or array
                if isinstance(active_ingredients, dict):
                    ingredient_name = active_ingredients.get("name", "")
                    if ingredient_name:
                        # Search for ANDA applications with this active ingredient
                        generic_query = (
                            f"application_number:ANDA* AND products.active_ingredients.name:{ingredient_name}"
                        )
                        generic_params: Any = {"search": generic_query, "limit": 20}

                        try:
                            generic_response = requests.get(base_url, params=generic_params)
                            generic_response.raise_for_status()
                            generic_data = generic_response.json()

                            if generic_data.get("results"):
                                generic_results.extend(generic_data["results"])
                        except requests.exceptions.RequestException:
                            continue  # Skip this ingredient if search fails

                elif isinstance(active_ingredients, list):
                    for ingredient in active_ingredients:
                        if isinstance(ingredient, dict):
                            ingredient_name = ingredient.get("name", "")
                            if ingredient_name:
                                # Search for ANDA applications with this active ingredient
                                generic_query = (
                                    f"application_number:ANDA* AND products.active_ingredients.name:{ingredient_name}"
                                )
                                generic_params = {"search": generic_query, "limit": 20}

                                try:
                                    generic_response = requests.get(base_url, params=generic_params)
                                    generic_response.raise_for_status()
                                    generic_data = generic_response.json()

                                    if generic_data.get("results"):
                                        generic_results.extend(generic_data["results"])
                                except requests.exceptions.RequestException:
                                    continue  # Skip this ingredient if search fails

        return {
            "brand_drug": brand_drug,
            "generic_equivalents": generic_results,
            "total_generics_found": len(generic_results),
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch generic equivalents: {e!s}"}
