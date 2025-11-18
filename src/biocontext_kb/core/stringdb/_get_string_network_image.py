from io import BytesIO
from typing import Annotated

import requests
from PIL import Image as PILImage
from fastmcp.utilities.types import Image
from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.stringdb._get_string_id import get_string_id


@core_mcp.tool()
def get_string_network_image(
    protein_symbol: Annotated[str, Field(description="Protein name to search for (e.g., 'TP53')")],
    species: Annotated[str, Field(description="Species taxonomy ID (e.g., '10090' for mouse)")],
    flavor: Annotated[
        str, Field(description="Network flavor (e.g., 'confidence', 'evidence', 'actions')")
    ] = "confidence",
    min_score: Annotated[int, Field(description="Minimum combined score threshold (0-1000)", ge=0, le=1000)] = 700,
) -> Image | dict:
    """Generate protein-protein interaction network image from STRING database. Always provide species parameter.

    Returns:
        Image or dict: Network visualization as PNG image object or error message.
    """
    # First resolve the protein name to a STRING ID
    try:
        string_id = get_string_id.fn(protein_symbol=protein_symbol, species=species)

        if not string_id or not isinstance(string_id, str):
            return {"error": f"No STRING ID found for protein: {protein_symbol}"}

        url = f"https://string-db.org/api/image/network?identifiers={string_id}&species={species}&required_score={min_score}&network_flavor={flavor}&format=png"
        response = requests.get(url)
        response.raise_for_status()
        img = PILImage.open(BytesIO(response.content))

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_bytes = buffer.getvalue()

        return Image(data=img_bytes, format="png")
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch image: {e!s}"}
    except Exception as e:
        return {"error": f"An error occurred: {e!s}"}
