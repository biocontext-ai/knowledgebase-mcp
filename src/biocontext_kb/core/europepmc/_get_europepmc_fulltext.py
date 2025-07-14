from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_europepmc_fulltext(
    pmc_id: Annotated[str, Field(description="PMC ID starting with 'PMC' (e.g., 'PMC11629965')")],
) -> dict:
    """Get the full text XML for a given PMC ID from Europe PMC.

    Args:
        pmc_id (str): PMC ID starting with "PMC" (e.g., "PMC11629965").

    Returns:
        dict: Full text XML content or error message
    """
    # Validate PMC ID format
    pmc_id = pmc_id.strip().upper()
    if not pmc_id or not pmc_id.startswith("PMC"):
        return {"error": "PMC ID must start with 'PMC'"}

    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc_id}/fullTextXML"

    try:
        response = requests.get(url)
        response.raise_for_status()

        # Return the XML content as a string
        return {"fulltext_xml": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch full text XML: {e!s}"}
