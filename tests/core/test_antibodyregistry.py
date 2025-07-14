import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_antibody_list_trpc6():
    """Test the tool get_antibody_list with TRPC6 gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_list", {"search": "TRPC6"})
        result = json.loads(result_text.content[0].text)

        assert "totalElements" in result
        assert "items" in result
        assert result["totalElements"] > 0
        assert len(result["items"]) > 0

        # Check structure of first antibody item
        first_item = result["items"][0]
        assert "abId" in first_item
        assert "catalogNum" in first_item
        assert "vendorName" in first_item
        assert "abTarget" in first_item


async def test_get_antibody_list_tp53():
    """Test the tool get_antibody_list with TP53 gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_list", {"search": "TP53"})
        result = json.loads(result_text.content[0].text)

        assert "totalElements" in result
        assert "items" in result
        assert result["totalElements"] > 0
        assert len(result["items"]) > 0


async def test_get_antibody_list_uniprot_id():
    """Test the tool get_antibody_list with UniProt ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_list", {"search": "P04637"})
        result = json.loads(result_text.content[0].text)

        assert "totalElements" in result
        assert "items" in result


async def test_get_antibody_list_empty_search():
    """Test the tool get_antibody_list with empty search term."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_list", {"search": ""})
        result = json.loads(result_text.content[0].text)

        assert "error" in result.keys()
        assert "Search term cannot be empty." in result["error"]


async def test_get_antibody_list_nonexistent_protein():
    """Test the tool get_antibody_list with nonexistent protein."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_list", {"search": "NONEXISTENTPROTEIN12345"})
        result = json.loads(result_text.content[0].text)

        assert "totalElements" in result
        assert "items" in result
        assert result["totalElements"] == 0
        assert len(result["items"]) == 0


async def test_get_antibody_information_valid_id():
    """Test the tool get_antibody_information with valid antibody ID."""
    async with Client(core_mcp) as client:
        # First get an antibody ID from a search
        search_result = (await client.call_tool("get_antibody_list", {"search": "TRPC6"})).data

        if search_result["totalElements"] > 0:
            ab_id = search_result["items"][0]["abId"]

            # Now get detailed information for this antibody
            result_text = await client.call_tool("get_antibody_information", {"ab_id": ab_id})
            result = json.loads(result_text.content[0].text)

            assert isinstance(result, dict)
            assert "abId" in result
            assert "vendorName" in result
            assert "abTarget" in result
            assert result["abId"] == ab_id


async def test_get_antibody_information_invalid_id():
    """Test the tool get_antibody_information with invalid antibody ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_information", {"ab_id": "invalid_id_12345"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_get_antibody_information_nonexistent_id():
    """Test the tool get_antibody_information with nonexistent antibody ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_antibody_information", {"ab_id": "9999999999"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result
        assert "No data found for antibody ID:" in result["error"]


async def test_antibody_workflow():
    """Test the complete workflow: search for antibodies then get detailed info."""
    async with Client(core_mcp) as client:
        # Step 1: Search for antibodies
        search_result = (await client.call_tool("get_antibody_list", {"search": "TP53"})).data

        assert search_result["totalElements"] > 0
        assert len(search_result["items"]) > 0

        # Step 2: Get detailed information for the first antibody
        first_antibody = search_result["items"][0]
        ab_id = first_antibody["abId"]

        detail_result = (await client.call_tool("get_antibody_information", {"ab_id": ab_id})).data

        # Verify the detailed information matches the search result
        assert isinstance(detail_result, dict)
        assert detail_result["abId"] == first_antibody["abId"]
        assert detail_result["catalogNum"] == first_antibody["catalogNum"]
        assert detail_result["vendorName"] == first_antibody["vendorName"]
