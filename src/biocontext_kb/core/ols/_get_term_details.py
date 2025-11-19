from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_term_details(
    term_id: Annotated[str, Field(description="Term ID in CURIE format (e.g., 'EFO:0000001', 'GO:0008150')")],
    ontology_id: Annotated[
        str, Field(description="Ontology ID where the term is defined (e.g., 'efo', 'go', 'chebi')")
    ],
) -> Dict[str, Any]:
    """Get comprehensive details about a specific ontology term including definition, synonyms, hierarchical relationships.

    Returns:
        dict: Term details with id, label, definition, synonyms, hierarchical info, num_descendants or error message.
    """
    if not term_id:
        return {"error": "term_id must be provided"}
    if not ontology_id:
        return {"error": "ontology_id must be provided"}

    # Double URL encode the term IRI
    import urllib.parse

    term_iri = f"http://purl.obolibrary.org/obo/{term_id.replace(':', '_')}"
    encoded_iri = urllib.parse.quote(urllib.parse.quote(term_iri, safe=""), safe="")

    url = f"https://www.ebi.ac.uk/ols4/api/v2/ontologies/{ontology_id}/entities/{encoded_iri}"

    try:
        response = requests.get(url)
        response.raise_for_status()

        data = response.json()

        if not data:
            return {"error": "Term not found"}

        # Extract comprehensive term information
        term_details = {
            "id": data.get("curie", "").replace(":", "_"),
            "curie": data.get("curie", ""),
            "label": data.get("label", ""),
            "definition": data.get("definition", ""),
            "synonyms": data.get("synonym", []),
            "ontology_name": data.get("ontologyName", ""),
            "ontology_prefix": data.get("ontologyPrefix", ""),
            "is_defining_ontology": data.get("isDefiningOntology", False),
            "is_obsolete": data.get("isObsolete", False),
            "is_preferred_root": data.get("isPreferredRoot", False),
            "has_hierarchical_children": data.get("hasHierarchicalChildren", False),
            "has_hierarchical_parents": data.get("hasHierarchicalParents", False),
            "has_direct_children": data.get("hasDirectChildren", False),
            "has_direct_parents": data.get("hasDirectParents", False),
            "num_descendants": data.get("numDescendants", 0),
            "num_hierarchical_descendants": data.get("numHierarchicalDescendants", 0),
            "appears_in": data.get("appearsIn", []),
            "defined_by": data.get("definedBy", []),
            "imported": data.get("imported", False),
        }

        return {"term_details": term_details}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch term details: {e!s}"}
