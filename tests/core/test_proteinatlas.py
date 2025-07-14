import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_human_protein_atlas_info_by_gene_id():
    """Test the tool get_human_protein_atlas_info with gene_id parameter."""
    async with Client(core_mcp) as client:
        # TP53 Ensembl ID
        result_text = await client.call_tool(
            "get_human_protein_atlas_info", {"gene_id": "ENSG00000141510", "gene_symbol": None}
        )
        result = json.loads(result_text.content[0].text)

        # Verify response structure
        assert "Gene" in result.keys()
        assert "Uniprot" in result.keys()

        # Check specific data for TP53
        assert result["Gene"] == "TP53"


async def test_get_human_protein_atlas_info_by_gene_symbol():
    """Test the tool get_human_protein_atlas_info with gene_symbol parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_human_protein_atlas_info", {"gene_id": None, "gene_symbol": "TP53"})
        result = json.loads(result_text.content[0].text)

        # Verify response structure
        assert "Gene" in result.keys()
        assert "Uniprot" in result.keys()

        # Check specific data for TP53
        assert result["Gene"] == "TP53"


async def test_get_human_protein_atlas_info_error_no_params():
    """Test the tool get_human_protein_atlas_info with no parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_human_protein_atlas_info", {"gene_id": None, "gene_symbol": None})
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert "error" in result.keys()
        assert "At least one of gene_id or gene_symbol must be provided" in result["error"]


async def test_get_human_protein_atlas_info_invalid_gene_symbol():
    """Test the tool get_human_protein_atlas_info with invalid gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_human_protein_atlas_info", {"gene_id": None, "gene_symbol": "NONEXISTENTGENE12345"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert "error" in result.keys()
