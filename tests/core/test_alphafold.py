import json

import pytest
import pytest_asyncio  # noqa: F401
from fastmcp import Client
from fastmcp.exceptions import ToolError

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.alphafold import get_alphafold_info_by_uniprot_id


async def test_get_alphafold_info_by_protein_symbol_valid():
    """Test the tool get_alphafold_info_by_protein_symbol with a valid protein symbol."""
    async with Client(core_mcp) as client:
        # Using TP53 gene symbol for human
        result = (
            await client.call_tool(
                "get_alphafold_info_by_protein_symbol", {"protein_symbol": "TP53", "species": "9606"}
            )
        ).data

        # Verify the response is a dict with links to PDB and CIF files
        assert isinstance(result, dict)
        assert "gene" in result
        assert "TP53" in result["gene"]
        assert "pdbUrl" in result
        assert "cifUrl" in result


async def test_get_alphafold_info_by_protein_symbol_invalid_symbol():
    """Test the tool get_alphafold_info_by_protein_symbol with a nonexistent protein symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_alphafold_info_by_protein_symbol", {"protein_symbol": "NONEXISTENTGENE12345", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert isinstance(result, dict)
        assert "error" in result
        assert "No results found for the given protein name" in result["error"]


async def test_get_alphafold_info_by_protein_symbol_missing_params():
    """Test the tool get_alphafold_info_by_protein_symbol is called with missing parameters."""
    async with Client(core_mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_alphafold_info_by_protein_symbol", {})


def test_get_alphafold_info_by_uniprot_id_valid():
    """Test the function get_alphafold_info_by_uniprot_id with a valid UniProt ID."""
    # Using Synpo UniProt ID for mouse (10090)
    result = get_alphafold_info_by_uniprot_id("Q497V1")

    # Verify the response is a list with links to PDB and CIF files
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert "gene" in result[0]
    assert result[0]["gene"] == "Synpo"
    assert "pdbUrl" in result[0]
    assert "cifUrl" in result[0]


def test_get_alphafold_info_by_uniprot_id_invalid_format():
    """Test the function get_alphafold_info_by_uniprot_id with an invalid UniProt ID format."""
    result = get_alphafold_info_by_uniprot_id("INVALID")

    # Verify error response
    assert isinstance(result, dict)
    assert "error" in result
    assert "Invalid UniProt ID format" in result["error"]


def test_get_alphafold_info_by_uniprot_id_nonexistent():
    """Test the function get_alphafold_info_by_uniprot_id with a nonexistent UniProt ID."""
    result = get_alphafold_info_by_uniprot_id("ABCDEF")

    # Verify error response
    assert isinstance(result, dict)
    assert "error" in result
    assert "Failed to fetch AlphaFold info: " in result["error"]
