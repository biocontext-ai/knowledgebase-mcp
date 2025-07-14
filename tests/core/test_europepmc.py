import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_europepmc_articles_by_query():
    """Test the tool get_europepmc_articles with query search."""
    async with Client(core_mcp) as client:
        result = (await client.call_tool("get_europepmc_articles", {"query": "pytximport"})).data

        assert isinstance(result, dict)
        assert "hitCount" in result.keys()
        assert "resultList" in result.keys()

        assert len(result["resultList"]["result"]) > 0
        assert (
            result["resultList"]["result"][0]["title"]
            == "Gene count estimation with pytximport enables reproducible analysis of bulk RNA sequencing data in Python."
        )


async def test_get_europepmc_articles_by_title():
    """Test the tool get_europepmc_articles with title search."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_articles", {"title": "RNA", "sort_by": "cited"})
        assert "hitCount" in result.data.keys()
        assert "resultList" in result.data.keys()


async def test_get_europepmc_articles_by_author():
    """Test the tool get_europepmc_articles with author search."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_articles", {"author": "kuehl,malte", "sort_by": "cited"})
        assert "hitCount" in result.data.keys()


async def test_get_europepmc_articles_combined():
    """Test the tool get_europepmc_articles with combined search."""
    async with Client(core_mcp) as client:
        result = await client.call_tool(
            "get_europepmc_articles", {"title": "RNA", "abstract": "sequencing", "search_type": "and"}
        )
        assert "hitCount" in result.data.keys()


async def test_get_europepmc_articles_no_params():
    """Test the tool get_europepmc_articles with no search parameters."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_articles", {})
        assert "error" in result.data.keys()
        assert "At least one of query, title, abstract, or author must be provided" in result.content[0].text


async def test_get_europepmc_fulltext():
    """Test the tool get_europepmc_fulltext with a valid PMC ID."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_fulltext", {"pmc_id": "PMC11629965"})
        assert "fulltext_xml" in result.data.keys()
        assert "<article" in result.content[0].text


async def test_get_europepmc_fulltext_invalid_id():
    """Test the tool get_europepmc_fulltext with an invalid PMC ID."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_fulltext", {"pmc_id": "invalid"})
        assert "error" in result.data.keys()
        assert "PMC" in result.content[0].text


async def test_get_europepmc_fulltext_nonexistent():
    """Test the tool get_europepmc_fulltext with a nonexistent PMC ID."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_europepmc_fulltext", {"pmc_id": "PMC999999999"})

        assert "error" in result.data.keys()
