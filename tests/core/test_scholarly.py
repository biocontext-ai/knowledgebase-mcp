import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_search_google_scholar_publications():
    """Test the tool search_google_scholar_publications."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "search_google_scholar_publications", {"query": "machine learning", "max_results": 3, "use_proxy": False}
        )

        # Check if we got results or an error (Google Scholar may block)
        if "error" in result.data:
            # If blocked, that's expected behavior - publication searches are risky
            assert "Google Scholar may be blocking" in result.content[0].text
        else:
            # If we got results, verify structure
            assert "query" in result.data
            assert "publications" in result.data
            assert isinstance(result.data["publications"], list)


async def test_search_google_scholar_publications_empty():
    """Test the tool search_google_scholar_publications with empty query."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "search_google_scholar_publications", {"query": "", "max_results": 3, "use_proxy": False}
        )

        # Should get an error or empty results
        assert "error" in result.data or result.data.get("total_found", 0) == 0


async def test_search_google_scholar_publications_by_author():
    """Test the tool search_google_scholar_publications with author field."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "search_google_scholar_publications", {"query": 'author:"Yann LeCun"', "max_results": 5, "use_proxy": False}
        )

        # Check if we got results or an error (Google Scholar may block)
        if "error" in result.data:
            # If blocked, that's expected behavior - publication searches are risky
            assert "Google Scholar may be blocking" in result.content[0].text
        else:
            # If we got results, verify structure
            assert "query" in result.data
            assert "publications" in result.data
            assert isinstance(result.data["publications"], list)
            assert result.data["query"] == 'author:"Yann LeCun"'
            # Should respect max_results limit
            assert len(result.data["publications"]) <= 5

            # Check that publications contain author information
            if result.data["publications"]:
                for pub in result.data["publications"]:
                    assert "author" in pub
                    assert "title" in pub


async def test_search_google_scholar_publications_author_with_topic():
    """Test the tool search_google_scholar_publications with author and topic."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "search_google_scholar_publications",
            {"query": 'author:"Geoffrey Hinton" deep learning', "max_results": 3, "use_proxy": False},
        )

        # Check if we got results or an error (Google Scholar may block)
        if "error" in result.data:
            # If blocked, that's expected behavior - publication searches are risky
            assert "Google Scholar may be blocking" in result.content[0].text
        else:
            # If we got results, verify structure
            assert "query" in result.data
            assert "publications" in result.data
            assert isinstance(result.data["publications"], list)
            assert result.data["query"] == 'author:"Geoffrey Hinton" deep learning'


async def test_search_google_scholar_publications_with_proxy():
    """Test the tool search_google_scholar_publications with proxy enabled."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "search_google_scholar_publications", {"query": "neural networks", "max_results": 3, "use_proxy": True}
        )

        # Check if we got results or an error (Google Scholar may block even with proxy)
        if "error" in result.data:
            # If blocked, that's expected behavior
            assert "Google Scholar may be blocking" in result.content[0].text
        else:
            # If we got results, verify structure
            assert "query" in result.data
            assert "publications" in result.data
            assert isinstance(result.data["publications"], list)
            assert result.data["query"] == "neural networks"
            # Should respect max_results limit
            assert len(result.data["publications"]) <= 3
