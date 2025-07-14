import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_panglaodb_options():
    """Test the tool get_panglaodb_options."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_options", {})
        result = json.loads(result_text.content[0].text)
        assert "organ" in result.keys()
        assert "cell_type" in result.keys()
        assert isinstance(result["organ"], list)
        assert isinstance(result["cell_type"], list)


async def test_get_panglaodb_marker_genes_by_species():
    """Test the tool get_panglaodb_marker_genes with species filter only."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_marker_genes", {"species": "Hs"})
        result = json.loads(result_text.content[0].text)
        assert "markers" in result.keys()
        assert isinstance(result["markers"], list)
        assert len(result["markers"]) > 0


async def test_get_panglaodb_marker_genes_by_organ():
    """Test the tool get_panglaodb_marker_genes with organ filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_marker_genes", {"species": "Hs", "organ": "brain"})
        result = json.loads(result_text.content[0].text)
        assert "markers" in result.keys()
        assert isinstance(result["markers"], list)
        assert len(result["markers"]) > 0
        # Check that all results contain the organ
        for marker in result["markers"]:
            assert "brain" in marker["organ"].lower()


async def test_get_panglaodb_marker_genes_by_cell_type():
    """Test the tool get_panglaodb_marker_genes with cell type filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_marker_genes", {"species": "Mm", "cell_type": "t cells"})
        result = json.loads(result_text.content[0].text)
        assert "markers" in result.keys()
        assert isinstance(result["markers"], list)
        assert len(result["markers"]) > 0
        # Check that all results contain the cell type
        for marker in result["markers"]:
            assert "t cells" in marker["cell type"].lower()


async def test_get_panglaodb_marker_genes_by_gene_symbol():
    """Test the tool get_panglaodb_marker_genes with gene symbol filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_marker_genes", {"species": "Hs", "gene_symbol": "CD19"})
        result = json.loads(result_text.content[0].text)
        assert "markers" in result.keys()
        assert isinstance(result["markers"], list)
        assert len(result["markers"]) > 0
        # Check that all results contain the gene symbol
        for marker in result["markers"]:
            assert "CD19" in marker["official gene symbol"]


async def test_get_panglaodb_marker_genes_with_all_params():
    """Test the tool get_panglaodb_marker_genes with all parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_panglaodb_marker_genes",
            {
                "species": "Hs",
                "min_sensitivity": 0.7,
                "min_specificity": 0.7,
                "organ": "blood",
                "cell_type": "b cells",
                "gene_symbol": "CD20",
            },
        )
        result = json.loads(result_text.content[0].text)
        assert "markers" in result.keys()
        assert isinstance(result["markers"], list)

        # If we have results, check that they match our filters
        if result["markers"]:
            for marker in result["markers"]:
                assert "blood" in marker["organ"].lower()
                assert "b cells" in marker["cell type"].lower()
                assert "CD20" in marker["official gene symbol"]
                assert marker["sensitivity_human"] >= 0.7
                assert marker["specificity_human"] >= 0.7


async def test_get_panglaodb_marker_genes_invalid_species():
    """Test the tool get_panglaodb_marker_genes with invalid species."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_panglaodb_marker_genes", {"species": "invalid"})
        result = json.loads(result_text.content[0].text)
        assert "error" in result.keys()
        assert "Invalid species" in result["error"]
