import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_search_grants_gov_with_keyword():
    """Test search_grants_gov with a keyword."""
    async with Client(core_mcp) as client:
        response = await client.call_tool("search_grants_gov", {"keyword": "neuroscience", "rows": 1})
        result = response.data
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "error" not in result, f"API returned an error: {result.get('error')}"
        assert "data" in result, "Response should contain 'data' key"
        assert "oppHits" in result["data"], "Response data should contain 'oppHits'"
        assert isinstance(result["data"]["oppHits"], list), "'oppHits' should be a list"

        if result["data"].get("hitCount", 0) > 0:
            assert len(result["data"]["oppHits"]) > 0, "Expected at least one hit for a common keyword if hitCount > 0"
            assert len(result["data"]["oppHits"]) <= 1, "Number of rows should be respected"
        elif result["data"].get("hitCount") == 0:
            assert len(result["data"]["oppHits"]) == 0, "oppHits should be empty if hitCount is 0"


async def test_search_grants_gov_with_agency_and_status():
    """Test search_grants_gov with agency and opportunity status."""
    async with Client(core_mcp) as client:
        response = await client.call_tool(
            "search_grants_gov",
            {
                "keyword": "bioinformatics",
                "agencies": "NIH",
                "opp_statuses": "posted",
                "rows": 2,
            },
        )
        result = response.data
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "error" not in result, f"API returned an error: {result.get('error')}"
        assert "data" in result, "Response should contain 'data' key"
        assert "oppHits" in result["data"], "Response data should contain 'oppHits'"
        assert isinstance(result["data"]["oppHits"], list), "'oppHits' should be a list"
        if result["data"].get("hitCount", 0) > 0 and len(result["data"]["oppHits"]) > 0:
            assert len(result["data"]["oppHits"]) <= 2, "Number of rows should be respected"


async def test_search_grants_gov_with_nonexistent_opp_num():
    """Test search_grants_gov with a non-existent opportunity number."""
    async with Client(core_mcp) as client:
        response = await client.call_tool(
            "search_grants_gov", {"opp_num": "THIS-OPP-NUM-DOES-NOT-EXIST-12345XYZ", "rows": 1}
        )
        result = response.data
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "error" not in result, f"API returned an error: {result.get('error')}"
        assert "data" in result, "Response should contain 'data' key"
        assert "oppHits" in result["data"], "Response data should contain 'oppHits'"
        assert isinstance(result["data"]["oppHits"], list), "'oppHits' should be a list"
        assert len(result["data"]["oppHits"]) == 0, "Expected 0 hits for a non-existent opportunity number"
        assert result["data"].get("hitCount", 0) == 0, "Expected hitCount to be 0 for a non-existent opportunity number"


async def test_search_grants_gov_no_params():
    """Test search_grants_gov with no parameters, relying on defaults."""
    async with Client(core_mcp) as client:
        response = await client.call_tool(
            "search_grants_gov",
            {},
        )
        result = response.data
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "error" not in result, f"API returned an error: {result.get('error')}"
        assert "data" in result, "Response should contain 'data' key"
        assert "oppHits" in result["data"], "Response data should contain 'oppHits'"
        assert isinstance(result["data"]["oppHits"], list), "'oppHits' should be a list"
        assert len(result["data"]["oppHits"]) <= 10, "Number of results should be at most the default row count (10)"
