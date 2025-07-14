import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_string_id():
    """Test the tool get_string_id with a valid protein name."""
    async with Client(core_mcp) as client:
        # Using TP53 as an example
        result_text = await client.call_tool("get_string_id", {"protein_symbol": "TP53", "species": "9606"})
        # Expected STRING ID for human TP53
        assert "9606.ENSP00000269305" in str(result_text.content[0].text)


async def test_get_string_id_preferred_name():
    """Test the tool get_string_id with return_field set to preferredName."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_string_id", {"protein_symbol": "TP53", "species": "9606", "return_field": "preferredName"}
        )
        assert "TP53" in str(result_text.content[0].text)


async def test_get_string_id_invalid_protein():
    """Test the tool get_string_id with an invalid protein name."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_string_id", {"protein_symbol": "NONEXISTENTPROTEIN12345"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_get_string_interactions():
    """Test the tool get_string_interactions with valid parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_string_interactions", {"protein_symbol": "TP53", "species": "9606"})
        result = json.loads(result_text.content[0].text)

        # Verify we get a list of interactions
        assert isinstance(result, list)
        assert len(result) > 0

        # Check for expected fields in the first interaction
        first_interaction = result[0]
        assert "stringId_A" in first_interaction
        assert "stringId_B" in first_interaction
        assert "score" in first_interaction


async def test_get_string_interactions_invalid_protein():
    """Test the tool get_string_interactions with an invalid protein name."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_string_interactions", {"protein_symbol": "NONEXISTENTPROTEIN12345", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_get_string_similarity_scores():
    """Test the tool get_string_similarity_scores with valid parameters."""
    async with Client(core_mcp) as client:
        # Compare dopamine receptors D1 and D2
        result_text = await client.call_tool(
            "get_string_similarity_scores",
            {"protein_symbol": "DRD1", "protein_symbol_comparison": "DRD2", "species": "9606"},
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get a list of similarity scores
        assert isinstance(result, list)

        # These proteins should have similarity scores
        if len(result) > 0:
            # Check for expected fields
            assert "stringId_A" in result[0]
            assert "stringId_B" in result[0]
            assert "bitscore" in result[0]


async def test_get_string_network_image():
    """Test the tool get_string_network_image with valid parameters."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_string_network_image", {"protein_symbol": "TP53", "species": "9606"})

        # Verify we get an image back
        assert result.content[0].type == "image"
        assert result.content[0].mimeType == "image/png"


async def test_get_string_network_image_invalid_protein():
    """Test the tool get_string_network_image with an invalid protein name."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_string_network_image", {"protein_symbol": "NONEXISTENTPROTEIN12345", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_get_string_id_mouse():
    """Test the tool get_string_id with a valid protein name for mouse species."""
    async with Client(core_mcp) as client:
        # Using Trp53 as mouse example (TP53 ortholog)
        result_text = await client.call_tool("get_string_id", {"protein_symbol": "Trp53", "species": "10090"})
        # Expected STRING ID pattern for mouse Trp53
        assert "10090.ENSMUSP" in str(result_text.content[0].text)


async def test_get_string_interactions_mouse():
    """Test the tool get_string_interactions with valid parameters for mouse species."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_string_interactions", {"protein_symbol": "Trp53", "species": "10090"})
        result = json.loads(result_text.content[0].text)

        # Verify we get a list of interactions
        assert isinstance(result, list)
        assert len(result) > 0

        # Check for expected fields in the first interaction
        first_interaction = result[0]
        assert "stringId_A" in first_interaction
        assert "stringId_B" in first_interaction
        assert "score" in first_interaction
        # Verify mouse species ID is present in the STRING IDs
        assert "10090." in first_interaction["stringId_A"]


async def test_get_string_network_image_mouse():
    """Test the tool get_string_network_image with valid parameters for mouse species."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_string_network_image", {"protein_symbol": "Trp53", "species": "10090"})

        # Verify we get an image back
        assert result.content[0].type == "image"
        assert result.content[0].mimeType == "image/png"
