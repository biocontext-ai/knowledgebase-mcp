import json

import pytest
import pytest_asyncio  # noqa: F401
from fastmcp import Client
from fastmcp.exceptions import ToolError

from biocontext_kb.core._server import core_mcp


async def test_get_reactome_info_by_identifier():
    """Test the tool get_reactome_info_by_identifier with a valid identifier."""
    async with Client(core_mcp) as client:
        # Using TP53 Uniprot ID
        result_text = await client.call_tool(
            "get_reactome_info_by_identifier", {"identifier": "P04637", "species": "Homo sapiens"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify response structure
        assert "pathways" in result
        assert isinstance(result["pathways"], list)

        # Ensure we got results
        assert len(result["pathways"]) > 0


async def test_get_reactome_info_by_identifier_with_filtering():
    """Test the tool get_reactome_info_by_identifier with additional filtering parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_reactome_info_by_identifier",
            {"identifier": "P04637", "species": "Homo sapiens", "page_size": 5, "include_disease": False},
        )
        result = json.loads(result_text.content[0].text)

        # Verify filtered results
        assert "pathways" in result
        assert len(result["pathways"]) <= 5


async def test_get_reactome_info_by_identifier_empty_id():
    """Test the tool get_reactome_info_by_identifier with an empty identifier."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_reactome_info_by_identifier", {"identifier": ""})
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert "error" in result
        assert "Identifier cannot be empty" in result["error"]


async def test_get_reactome_info_by_identifier_invalid_order():
    """Test the tool get_reactome_info_by_identifier with an invalid order parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_reactome_info_by_identifier", {"identifier": "P04637", "order": "INVALID_ORDER"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert "error" in result
        assert "Order must be either 'ASC' or 'DESC'" in result["error"]


async def test_get_reactome_info_by_identifier_invalid_p_value():
    """Test the tool get_reactome_info_by_identifier with an invalid p_value parameter."""
    async with Client(core_mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "get_reactome_info_by_identifier",
                {
                    "identifier": "P04637",
                    "p_value": 2.0,  # Invalid: p_value > 1
                },
            )
