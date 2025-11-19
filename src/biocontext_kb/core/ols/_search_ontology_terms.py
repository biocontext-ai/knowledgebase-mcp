from typing import Annotated, Any, Dict, List

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def search_ontology_terms(
    search_term: Annotated[str, Field(description="Term to search for")],
    ontologies: Annotated[
        str,
        Field(
            description="Comma-separated ontology IDs (e.g., 'efo,go,chebi'). Leave empty for all. Use get_available_ontologies() to see options"
        ),
    ] = "",
    size: Annotated[
        int,
        Field(description="Maximum number of results to return"),
    ] = 20,
    exact_match: Annotated[
        bool,
        Field(description="Whether to perform exact match search"),
    ] = False,
) -> Dict[str, Any]:
    """Search for terms across multiple ontologies in OLS. Use get_available_ontologies() first to discover ontologies.

    Returns:
        dict: Terms array, terms_by_ontology grouped results, total_results, ontologies_found list or error message.
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
