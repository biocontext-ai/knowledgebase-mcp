import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_recent_biorxiv_preprints_recent():
    """Test the tool get_recent_biorxiv_preprints with recent count."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "biorxiv", "recent_count": 5, "max_results": 5}
        )

        assert isinstance(result.data, dict)
        assert "error" not in result.data, f"Unexpected error: {result.data.get('error', '')}"
        assert "server" in result.data
        assert "papers" in result.data
        assert "total_returned" in result.data
        assert "search_params" in result.data
        assert isinstance(result.data["papers"], list)
        assert result.data["server"] == "biorxiv"
        assert len(result.data["papers"]) <= 5  # Should not exceed max_results

        # Validate paper structure if papers are returned
        for paper in result.data["papers"]:
            assert isinstance(paper, dict)
            assert "title" in paper
            assert "authors" in paper
            assert "doi" in paper
            assert "date" in paper


async def test_get_recent_biorxiv_preprints_date_range():
    """Test the tool get_recent_biorxiv_preprints with date range."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints",
            {"server": "biorxiv", "start_date": "2024-01-01", "end_date": "2024-01-02", "max_results": 3},
        )

        assert isinstance(result.data, dict)
        assert "error" not in result.data, f"Unexpected error: {result.data.get('error', '')}"
        assert "server" in result.data
        assert "papers" in result.data
        assert "search_params" in result.data
        assert "total_returned" in result.data
        assert result.data["server"] == "biorxiv"
        assert isinstance(result.data["papers"], list)
        assert len(result.data["papers"]) <= 3  # Should not exceed max_results

        # Check that search params contain the interval
        search_params = result.data["search_params"]
        assert "interval" in search_params
        assert search_params["interval"] == "2024-01-01/2024-01-02"


async def test_get_recent_biorxiv_preprints_days():
    """Test the tool get_recent_biorxiv_preprints with days parameter."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "medrxiv", "days": 7, "max_results": 5}
        )

        assert isinstance(result.data, dict)
        assert "error" not in result.data, f"Unexpected error: {result.data.get('error', '')}"
        assert "server" in result.data
        assert "papers" in result.data
        assert "search_params" in result.data
        assert "total_returned" in result.data
        assert result.data["server"] == "medrxiv"
        assert isinstance(result.data["papers"], list)
        assert len(result.data["papers"]) <= 5  # Should not exceed max_results

        # Check that search params contain interval (converted from days)
        search_params = result.data["search_params"]
        assert "interval" in search_params
        assert "original_days" in search_params
        assert search_params["original_days"] == 7

        # Validate interval format (should be YYYY-MM-DD/YYYY-MM-DD)
        import re

        interval_pattern = r"^\d{4}-\d{2}-\d{2}/\d{4}-\d{2}-\d{2}$"
        assert re.match(interval_pattern, search_params["interval"])


async def test_get_recent_biorxiv_preprints_invalid_server():
    """Test the tool get_recent_biorxiv_preprints with invalid server."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_recent_biorxiv_preprints", {"server": "invalid", "recent_count": 5})

        assert "error" in result.data
        assert "Server must be 'biorxiv' or 'medrxiv'" in result.data["error"]


async def test_get_recent_biorxiv_preprints_no_search_params():
    """Test the tool get_recent_biorxiv_preprints without search parameters."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_recent_biorxiv_preprints", {"server": "biorxiv"})

        assert "error" in result.data
        assert "Specify exactly one" in result.data["error"]


async def test_get_biorxiv_preprint_details():
    """Test the tool get_biorxiv_preprint_details with a known DOI."""
    async with Client(core_mcp) as client:
        # Use a known valid bioRxiv DOI that should exist
        test_doi = "10.1101/2025.05.21.653987"

        result = await client.call_tool("get_biorxiv_preprint_details", {"doi": test_doi, "server": "biorxiv"})

        assert isinstance(result.data, dict)

        # With a valid DOI, we should not get errors
        assert "error" not in result.data, f"Unexpected error: {result.data.get('error', '')}"

        # Check for expected fields in successful response (direct fields, not in collection)
        assert "doi" in result.data
        assert "title" in result.data
        assert "authors" in result.data
        assert "category" in result.data
        assert "abstract" in result.data
        assert "server" in result.data

        # Validate the DOI matches what we requested
        assert result.data["doi"] == test_doi
        assert result.data["server"] == "biorxiv"


async def test_get_biorxiv_preprint_details_invalid_server():
    """Test the tool get_biorxiv_preprint_details with invalid server."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_biorxiv_preprint_details", {"doi": "10.1101/test", "server": "invalid"})

        assert "error" in result.data
        assert "Server must be 'biorxiv' or 'medrxiv'" in result.data["error"]


async def test_get_recent_biorxiv_preprints_with_category():
    """Test the tool get_recent_biorxiv_preprints with category filter."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints",
            {"server": "biorxiv", "days": 30, "category": "bioinformatics", "max_results": 3},
        )

        assert isinstance(result.data, dict)
        assert "error" not in result.data, f"Unexpected error: {result.data.get('error', '')}"
        assert "server" in result.data
        assert "papers" in result.data
        assert "search_params" in result.data
        assert result.data["server"] == "biorxiv"

        # Check that category is included in search params
        search_params = result.data["search_params"]
        assert "category" in search_params
        assert search_params["category"] == "bioinformatics"


async def test_get_recent_biorxiv_preprints_invalid_date_format():
    """Test the tool get_recent_biorxiv_preprints with invalid date format."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "biorxiv", "start_date": "2024/01/01", "end_date": "2024/01/02"}
        )

        assert isinstance(result.data, dict)
        assert "error" in result.data
        assert "YYYY-MM-DD format" in result.data["error"]


async def test_get_recent_biorxiv_preprints_invalid_date_range():
    """Test the tool get_recent_biorxiv_preprints with invalid date range (end before start)."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "biorxiv", "start_date": "2024-01-10", "end_date": "2024-01-05"}
        )

        assert isinstance(result.data, dict)
        assert "error" in result.data
        assert "Start date must be before or equal to end date" in result.data["error"]


async def test_get_recent_biorxiv_preprints_multiple_params():
    """Test the tool get_recent_biorxiv_preprints with multiple conflicting parameters."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_recent_biorxiv_preprints", {"server": "biorxiv", "recent_count": 5, "days": 7}
        )

        assert isinstance(result.data, dict)
        assert "error" in result.data
        assert "Specify exactly one" in result.data["error"]


async def test_get_recent_biorxiv_preprints_zero_max_results():
    """Test the tool get_recent_biorxiv_preprints with zero max_results."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool(
                "get_recent_biorxiv_preprints", {"server": "biorxiv", "recent_count": 5, "max_results": 0}
            )
            # If we get here, the test should fail
            raise AssertionError("Expected ToolError for max_results=0")
        except Exception as e:
            # Should get a validation error about minimum value
            assert "minimum of 1" in str(e)


async def test_get_recent_biorxiv_preprints_negative_days():
    """Test the tool get_recent_biorxiv_preprints with negative days."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool("get_recent_biorxiv_preprints", {"server": "biorxiv", "days": -5})
            # If we get here, the test should fail
            raise AssertionError("Expected ToolError for negative days")
        except Exception as e:
            # Should get a validation error about minimum value
            assert "minimum of 1" in str(e)


async def test_get_biorxiv_preprint_details_malformed_doi():
    """Test the tool get_biorxiv_preprint_details with malformed DOI."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_biorxiv_preprint_details", {"doi": "not-a-doi", "server": "biorxiv"})

        assert isinstance(result.data, dict)
        # For a malformed DOI, the API should return a structured response indicating no results found
        # The function should handle this gracefully without system errors
        assert "error" in result.data
        # Should be a meaningful error message about the DOI not being found
        error_msg = result.data["error"].lower()
        assert "not found" in error_msg or "no preprint found" in error_msg


async def test_get_biorxiv_preprint_details_missing_doi():
    """Test the tool get_biorxiv_preprint_details with missing DOI."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool("get_biorxiv_preprint_details", {"server": "biorxiv"})
            # If we get here, the test should fail
            raise AssertionError("Expected ToolError for missing DOI")
        except Exception as e:
            # Should get a validation error about required property
            assert "required property" in str(e)
