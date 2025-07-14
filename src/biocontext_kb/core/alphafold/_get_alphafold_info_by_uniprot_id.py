import re
from typing import Annotated

import requests
from pydantic import Field


def get_alphafold_info_by_uniprot_id(
    uniprot_id: Annotated[str, Field(description="The UniProt ID of the protein (e.g., 'P62258')")],
) -> dict:
    """Query the AlphaFold database for the protein structure information using the UniProt ID.

    Args:
        uniprot_id (str): The UniProt ID of the protein (e.g., "P62258").

    Returns:
        dict: Protein structure information or an error message.
    """
    # Ensure the UniProt ID is in uppercase
    uniprot_id = uniprot_id.upper()

    # Validate the UniProt ID format
    if not re.match(r"^[A-Z0-9]{6}$", uniprot_id):
        return {"error": "Invalid UniProt ID format"}

    # Construct the URL for AlphaFold database query
    url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"

    try:
        # Make the request and get the response
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch AlphaFold info: {e!s}"}
