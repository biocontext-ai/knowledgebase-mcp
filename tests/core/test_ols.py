import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_efo_id_by_disease_name():
    """Test the tool get_efo_id_by_disease_name."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_efo_id_by_disease_name", {"disease_name": "diabetes"})
        result = result_raw.data
        assert result.get("efo_ids")
        assert len(result["efo_ids"]) > 0
        # Check that the first result has expected structure
        first_result = result["efo_ids"][0]
        assert "id" in first_result
        assert "label" in first_result
        assert "description" in first_result
        assert first_result["id"].startswith("EFO_")


async def test_get_efo_id_by_disease_name_not_found():
    """Test the tool get_efo_id_by_disease_name with a non-existent disease name."""
    async with Client(core_mcp) as client:
        # Using a made-up disease name that shouldn't exist in EFO
        result = await client.call_tool("get_efo_id_by_disease_name", {"disease_name": "xyznonexistentdisease12345"})
        assert "error" in result.content[0].text
        assert "No results found" in result.content[0].text


async def test_get_efo_id_by_disease_name_empty():
    """Test the tool get_efo_id_by_disease_name with an empty disease name."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_efo_id_by_disease_name", {"disease_name": ""})
        assert "error" in result.content[0].text
        assert "disease_name must be provided" in result.content[0].text
