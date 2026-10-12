import json

import pytest
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_uniprot_protein_info_by_protein_id():
    """Test the tool get_uniprot_protein_info with protein_id parameter."""
    async with Client(core_mcp) as client:
        # Using TP53 UniProt ID
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": "P04637", "protein_name": None, "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "primaryAccession" in result
        assert result["primaryAccession"] == "P04637"


async def test_get_uniprot_protein_info_by_protein_name():
    """Test the tool get_uniprot_protein_info with protein_name parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": None, "protein_name": "P53", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "primaryAccession" in result
        assert result["primaryAccession"] == "P04637"


async def test_get_uniprot_protein_info_by_gene_symbol():
    """Test the tool get_uniprot_protein_info with gene_symbol parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info",
            {"protein_id": None, "protein_name": None, "gene_symbol": "TP53", "species": "9606"},
        )
        result = json.loads(result_text.content[0].text)

        assert "primaryAccession" in result
        assert result["primaryAccession"] == "P04637"


async def test_get_uniprot_protein_info_both_parameters():
    """Test the tool get_uniprot_protein_info with both protein_id and protein_name.

    This should prioritize protein_id.
    """
    async with Client(core_mcp) as client:
        # Using TP53 UniProt ID and a different protein name
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": "P04637", "protein_name": "SYNPO", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "primaryAccession" in result
        assert result["primaryAccession"] == "P04637"


async def test_get_uniprot_protein_info_mouse_species():
    """Test the tool get_uniprot_protein_info with mouse species (taxonomy ID)."""
    async with Client(core_mcp) as client:
        # Using mouse Trp53 gene
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": None, "protein_name": "Trp53", "species": "10090"}
        )
        result = json.loads(result_text.content[0].text)

        assert "organism" in result
        assert result["organism"]["taxonId"] == 10090


async def test_get_uniprot_protein_info_species_name():
    """Test the tool get_uniprot_protein_info with species name instead of taxonomy ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": None, "protein_name": "TP53", "species": "Homo sapiens"}
        )
        result = json.loads(result_text.content[0].text)

        assert "organism" in result.keys()
        assert "taxonId" in result["organism"].keys()
        assert result["organism"]["taxonId"] == 9606


async def test_get_uniprot_protein_info_no_species():
    """Test the tool get_uniprot_protein_info without species parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": "P04637", "protein_name": None, "species": None}
        )
        result = json.loads(result_text.content[0].text)

        # Should still work but may return results from multiple species
        assert "primaryAccession" in result.keys()


async def test_get_uniprot_protein_info_error_no_params():
    """Test the tool get_uniprot_protein_info with no protein identification parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": None, "protein_name": None, "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify error response
        assert "error" in result.keys()
        assert "At least one of protein_id or protein_name or gene_symbol must be provided" in result["error"]


async def test_get_uniprot_protein_info_invalid_protein_id():
    """Test the tool get_uniprot_protein_info with invalid protein ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": "INVALIDPROTEINID12345", "protein_name": None, "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        # Should return an error
        assert "error" in result.keys()
        assert isinstance(result["error"], str)
        assert "Exception occurred" in result["error"]


async def test_get_uniprot_protein_info_invalid_protein_name():
    """Test the tool get_uniprot_protein_info with invalid protein name."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info",
            {"protein_id": None, "protein_name": "NONEXISTENTPROTEIN12345", "species": "9606"},
        )
        result = json.loads(result_text.content[0].text)

        # Should return empty results for invalid protein name
        assert "error" in result.keys()
        assert "No results found for the given query." in result["error"]


async def test_get_uniprot_protein_info_invalid_species():
    """Test the tool get_uniprot_protein_info with invalid species."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": "P04637", "protein_name": None, "species": "99999"}
        )
        result = json.loads(result_text.content[0].text)

        assert "error" in result.keys()
        assert "No results found for the given query." in result["error"]


async def test_get_uniprot_protein_info_case_sensitivity():
    """Test the tool get_uniprot_protein_info with different case protein names."""
    async with Client(core_mcp) as client:
        # Test with lowercase protein name
        result_text = await client.call_tool(
            "get_uniprot_protein_info", {"protein_id": None, "protein_name": "p53", "species": "9606"}
        )
        result = json.loads(result_text.content[0].text)

        assert "primaryAccession" in result
        assert result["primaryAccession"] == "P04637"


async def test_get_uniprot_id_by_protein_symbol_valid():
    """Test the tool get_uniprot_id_by_protein_symbol with a valid protein symbol."""
    async with Client(core_mcp) as client:
        # Using TP53 gene symbol for human (9606); a protein name search would return TP53TG5 (Q9Y2B4) instead (#5)
        result = (
            await client.call_tool("get_uniprot_id_by_protein_symbol", {"protein_symbol": "TP53", "species": "9606"})
        ).data

        assert result["accession"] == "P04637"
        assert result["gene"] == "TP53"
        assert result["reviewed"] is True
        assert result["match_type"] == "gene"


@pytest.mark.parametrize(
    ("protein_symbol", "species", "accession", "match_type"),
    [
        ("NPHS2", "9606", "Q9NP85", "gene"),
        ("Nphs2", "10090", "Q91X05", "gene"),
        ("SYNPO", "9606", "Q8N3V7", "gene"),
        ("p53", "9606", "P04637", "synonym"),
        ("Podocin", "9606", "Q9NP85", "protein_name"),
        # gene_exact also matches the unreviewed gene "serum albumin" (Q16167); only exact names count
        ("albumin", "9606", "P02768", "protein_name"),
    ],
)
async def test_get_uniprot_id_by_protein_symbol_canonical_entry(protein_symbol, species, accession, match_type):
    """Test that the tool returns the reviewed canonical entry for the cases reported in #5."""
    async with Client(core_mcp) as client:
        result = (
            await client.call_tool(
                "get_uniprot_id_by_protein_symbol", {"protein_symbol": protein_symbol, "species": species}
            )
        ).data

        assert result["accession"] == accession
        assert result["reviewed"] is True
        assert result["match_type"] == match_type


async def test_get_uniprot_id_by_protein_symbol_ambiguous():
    """Test that an ambiguous symbol returns all reviewed candidates instead of picking one."""
    async with Client(core_mcp) as client:
        # CDKN2A encodes both p16INK4a (P42771) and p14ARF (Q8N726)
        result = (
            await client.call_tool("get_uniprot_id_by_protein_symbol", {"protein_symbol": "CDKN2A", "species": "9606"})
        ).data

        assert "error" in result
        assert {c["accession"] for c in result["candidates"]} == {"P42771", "Q8N726"}


async def test_get_uniprot_id_by_protein_symbol_unreviewed_fallback():
    """Test the fallback to unreviewed entries when no reviewed entry exists."""
    async with Client(core_mcp) as client:
        # Zebrafish nphs2 has no Swiss-Prot entry
        result = (
            await client.call_tool("get_uniprot_id_by_protein_symbol", {"protein_symbol": "nphs2", "species": "7955"})
        ).data

        assert result["reviewed"] is False
        assert result["gene"] == "nphs2"
        assert result["match_type"] == "gene"


async def test_get_uniprot_id_by_protein_symbol_partial_name():
    """Test that partial protein name matches are listed as candidates instead of picking one."""
    async with Client(core_mcp) as client:
        result = (
            await client.call_tool(
                "get_uniprot_id_by_protein_symbol", {"protein_symbol": "hemoglobin", "species": "9606"}
            )
        ).data

        assert "No exact match" in result["error"]
        assert result["candidates"]
        assert all("emoglobin" in c["protein_name"] for c in result["candidates"])


async def test_get_uniprot_id_by_protein_symbol_invalid_symbol():
    """Test the tool get_uniprot_id_by_protein_symbol with a nonexistent protein symbol."""
    async with Client(core_mcp) as client:
        result = (
            await client.call_tool(
                "get_uniprot_id_by_protein_symbol", {"protein_symbol": "NONEXISTENTGENE12345", "species": "9606"}
            )
        ).data

        assert "No UniProt entry found" in result["error"]


async def test_get_uniprot_id_by_protein_symbol_empty_symbol():
    """Test the tool get_uniprot_id_by_protein_symbol with a symbol that is empty after sanitizing."""
    async with Client(core_mcp) as client:
        result = (
            await client.call_tool("get_uniprot_id_by_protein_symbol", {"protein_symbol": ' " ', "species": "9606"})
        ).data

        assert result == {"error": "protein_symbol must not be empty."}


async def test_get_uniprot_id_by_protein_symbol_missing_params():
    """Test the tool get_uniprot_id_by_protein_symbol with missing parameters."""
    async with Client(core_mcp) as client:
        # This should raise a ToolError due to missing required parameter
        with pytest.raises(Exception):  # Will be a validation error # noqa: B017
            await client.call_tool("get_uniprot_id_by_protein_symbol", {})
