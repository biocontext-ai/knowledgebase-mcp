import logging
from typing import Annotated, Any, Dict

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp

logger = logging.getLogger(__name__)


@core_mcp.tool()
def get_biorxiv_preprint_details(
    doi: Annotated[str, Field(description="DOI of the preprint (e.g., '10.1101/2020.09.09.20191205')")],
    server: Annotated[str, Field(description="Server to search: 'biorxiv' or 'medrxiv'")] = "biorxiv",
) -> Dict[str, Any]:
    """Get detailed information about a specific preprint by DOI.

    This tool retrieves detailed metadata for a single preprint from bioRxiv or medRxiv
    using its DOI identifier.

    Args:
        doi (str): DOI of the preprint (e.g., '10.1101/2020.09.09.20191205').
        server (str): Server to search - 'biorxiv' or 'medrxiv' (default: 'biorxiv').

    Returns:
        dict: Detailed preprint information or error message
    """
    # Validate server
    if server.lower() not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be 'biorxiv' or 'medrxiv'"}

    server = server.lower()

    # Clean DOI - remove URL prefix if present
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    elif doi.startswith("doi:"):
        doi = doi.replace("doi:", "")

    try:
        # Build URL for single DOI lookup
        url = f"https://api.biorxiv.org/details/{server}/{doi}/na/json"

        # Make request
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Check if paper was found
        collection = data.get("collection", [])
        if not collection:
            return {"error": f"No preprint found with DOI {doi} on {server}", "messages": data.get("messages", [])}

        # Get the paper details
        paper = collection[0]

        # Return structured paper information
        result = {
            "doi": paper.get("doi", ""),
            "title": paper.get("title", ""),
            "authors": paper.get("authors", ""),
            "corresponding_author": paper.get("author_corresponding", ""),
            "corresponding_institution": paper.get("author_corresponding_institution", ""),
            "date": paper.get("date", ""),
            "version": paper.get("version", ""),
            "type": paper.get("type", ""),
            "license": paper.get("license", ""),
            "category": paper.get("category", ""),
            "abstract": paper.get("abstract", ""),
            "published": paper.get("published", ""),
            "server": paper.get("server", server),
            "jats_xml_path": paper.get("jats", ""),
        }

        return result

    except requests.exceptions.RequestException as e:
        logger.error(f"Error retrieving preprint {doi} from {server}: {e}")
        return {"error": f"Failed to retrieve preprint from {server}: {e!s}"}
    except Exception as e:
        logger.error(f"Unexpected error retrieving preprint {doi}: {e}")
        return {"error": f"Unexpected error: {e!s}"}
