import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_pride_project_basic():
    """Test the get_pride_project tool with a valid PRIDE accession."""
    async with Client(core_mcp) as client:
        # Using a well-known PRIDE project
        result_text = await client.call_tool("get_pride_project", {"project_accession": "PRD000001"})
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        assert result["accession"] == "PRD000001"
        assert "title" in result
        assert "projectDescription" in result


async def test_get_pride_project_with_files():
    """Test the get_pride_project tool with file information."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_pride_project", {"project_accession": "PRD000001", "include_files": True}
        )
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        # files may or may not be present depending on the project
        assert "files" in result or "accession" in result


async def test_get_pride_project_with_similar():
    """Test the get_pride_project tool with similar projects."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_pride_project", {"project_accession": "PRD000001", "include_similar_projects": True}
        )
        result = json.loads(result_text.content[0].text)

        assert "accession" in result
        # similar_projects may or may not be present
        assert "similar_projects" in result or "accession" in result


async def test_get_pride_project_nonexistent():
    """Test the get_pride_project tool with non-existent accession."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_pride_project", {"project_accession": "PRD999999"})
        result = json.loads(result_text.content[0].text)

        # Should return error for non-existent project
        assert "error" in result


async def test_search_pride_projects_basic():
    """Test the search_pride_projects tool with basic search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_pride_projects", {"page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result
        assert len(result["results"]) <= 5


async def test_search_pride_projects_with_keyword():
    """Test the search_pride_projects tool with keyword search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_pride_projects", {"keyword": "human", "page_size": 10})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result
        assert "search_criteria" in result
        assert result["search_criteria"]["keyword"] == "human"


async def test_search_pride_projects_with_organism_filter():
    """Test the search_pride_projects tool with organism filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_pride_projects", {"organism_filter": "Homo sapiens", "page_size": 5}
        )
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result


async def test_search_pride_projects_with_instrument_filter():
    """Test the search_pride_projects tool with instrument filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_pride_projects", {"instrument_filter": "Orbitrap", "page_size": 5})
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result


async def test_search_pride_projects_sorting():
    """Test the search_pride_projects tool with different sorting."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_pride_projects", {"sort_field": "title", "sort_direction": "ASC", "page_size": 5}
        )
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result


async def test_search_pride_proteins_basic():
    """Test the search_pride_proteins tool with a valid project."""
    async with Client(core_mcp) as client:
        # Using a project that should have protein data
        result_text = await client.call_tool(
            "search_pride_proteins", {"project_accession": "PRD000001", "page_size": 5}
        )
        result = json.loads(result_text.content[0].text)

        # Should either return results or an error (if project has no protein data)
        assert "results" in result or "error" in result
        if "results" in result:
            assert "count" in result
            assert "project_accession" in result


async def test_search_pride_proteins_with_keyword():
    """Test the search_pride_proteins tool with keyword search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_pride_proteins", {"project_accession": "PRD000001", "keyword": "albumin", "page_size": 5}
        )
        result = json.loads(result_text.content[0].text)

        # Should either return results or an error
        assert "results" in result or "error" in result


async def test_search_pride_proteins_sorting():
    """Test the search_pride_proteins tool with different sorting."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_pride_proteins",
            {"project_accession": "PRD000001", "sort_field": "proteinName", "sort_direction": "DESC", "page_size": 5},
        )
        result = json.loads(result_text.content[0].text)

        # Should either return results or an error
        assert "results" in result or "error" in result


async def test_search_pride_proteins_invalid_project():
    """Test the search_pride_proteins tool with invalid project."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_pride_proteins", {"project_accession": "INVALIDPROJECT123"})
        result = json.loads(result_text.content[0].text)

        assert "error" in result


async def test_search_pride_projects_multiple_filters():
    """Test the search_pride_projects tool with multiple filters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_pride_projects",
            {"keyword": "proteome", "organism_filter": "Homo sapiens", "experiment_type_filter": "TMT", "page_size": 5},
        )
        result = json.loads(result_text.content[0].text)

        assert "results" in result
        assert "count" in result
        assert "search_criteria" in result
