from typing import Annotated, Any, Dict, List

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_ontology_terms(
    search_term: Annotated[str, Field(description="The term to search for across all ontologies")],
    ontologies: Annotated[
        str,
        Field(
            description="Comma-separated list of ontology IDs to search in (e.g., 'efo,go,chebi'). Leave empty to search all ontologies. Use get_available_ontologies() to see all available ontology IDs."
        ),
    ] = "",
    size: Annotated[
        int,
        Field(description="The maximum number of results to return"),
    ] = 20,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform an exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Query the Ontology Lookup Service (OLS) for terms across multiple ontologies.

    This function provides a general search across ontologies in OLS, allowing you to
    find terms from multiple ontologies or search all ontologies at once.

    TIP: Use get_available_ontologies() first to discover which ontologies are available
    and their IDs before searching.

    Args:
        search_term (str): The term to search for.
        ontologies (str): Comma-separated ontology IDs (e.g., "efo,go,chebi"). Empty for all.
                         Use get_available_ontologies() to see available options.
        size (int): Maximum number of results to return (default: 20).
        exact_match (bool): Whether to perform an exact match search (default: False).

    Returns:
        dict: Dictionary containing terms from various ontologies or error message
    """
    if not search_term:
        return {"error": "search_term must be provided"}

    url = "https://www.ebi.ac.uk/ols4/api/v2/entities"

    params = {
        "search": search_term,
        "size": str(size),
        "lang": "en",
        "exactMatch": str(exact_match).lower(),
        "includeObsoleteEntities": "false",
    }

    # Add ontology filter if specified
    if ontologies.strip():
        # Convert comma-separated string to individual ontologyId parameters
        ontology_list = [ont.strip() for ont in ontologies.split(",") if ont.strip()]
        if ontology_list:
            params["ontologyId"] = ",".join(ontology_list)

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()

        if not data.get("elements"):
            return {"error": "No terms found"}

        # Extract terms with comprehensive information
        terms = [
            {
                "id": element.get("curie", "").replace(":", "_"),
                "curie": element.get("curie", ""),
                "label": element.get("label", ""),
                "definition": element.get("definition", ""),
                "synonyms": element.get("synonym", []),
                "ontology_name": element.get("ontologyName", ""),
                "ontology_prefix": element.get("ontologyPrefix", ""),
                "is_defining_ontology": element.get("isDefiningOntology", False),
                "is_obsolete": element.get("isObsolete", False),
                "has_hierarchical_children": element.get("hasHierarchicalChildren", False),
                "has_hierarchical_parents": element.get("hasHierarchicalParents", False),
                "num_descendants": element.get("numDescendants", 0),
                "appears_in": element.get("appearsIn", []),
            }
            for element in data["elements"]
        ]

        # Group results by ontology for better organization
        results_by_ontology: Dict[str, List[Dict[str, Any]]] = {}
        for term in terms:
            ontology = term["ontology_name"] or term["ontology_prefix"] or "unknown"
            if ontology not in results_by_ontology:
                results_by_ontology[ontology] = []
            results_by_ontology[ontology].append(term)

        return {
            "terms": terms,
            "terms_by_ontology": results_by_ontology,
            "total_results": len(terms),
            "ontologies_found": list(results_by_ontology.keys()),
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to search ontology terms: {e!s}"}
