import json

import pytest
import pytest_asyncio  # noqa: F401
from fastmcp import Client
from fastmcp.exceptions import ToolError

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.kegg._query_kegg import KeggDatabase, KeggOperation, KeggOption


async def test_get_kegg_id_by_gene_symbol():
    """Test the tool get_kegg_id_by_gene_symbol with a valid gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_kegg_id_by_gene_symbol", {"gene_symbol": "TP53", "organism_code": "9606"}
        )
        # The response contains the human TP53 KEGG ID
        assert "hsa:7157" in str(result_text.content[0].text)


async def test_get_kegg_id_by_gene_symbol_mouse():
    """Test the tool get_kegg_id_by_gene_symbol with a mouse gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_kegg_id_by_gene_symbol", {"gene_symbol": "Trp53", "organism_code": "10090"}
        )
        # The response contains the mouse Trp53 KEGG ID
        assert "mmu:22059" in str(result_text.content[0].text)


async def test_get_kegg_id_by_gene_symbol_missing_parameters():
    """Test the tool get_kegg_id_by_gene_symbol with missing parameters."""
    async with Client(core_mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool("get_kegg_id_by_gene_symbol", {"gene_symbol": "TP53"})


async def test_get_kegg_id_by_gene_symbol_invalid_gene():
    """Test the tool get_kegg_id_by_gene_symbol with an invalid gene symbol."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_kegg_id_by_gene_symbol", {"gene_symbol": "NONEXISTENTGENE12345", "organism_code": "9606"}
        )
        result = json.loads(result_text.content[0].text)
        # Should return an error about the gene not being found
        assert "error" in result


async def test_query_kegg_list_pathways():
    """Test the tool query_kegg for listing human pathways."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.LIST,
                "database": KeggDatabase.PATHWAY,
                "query": "hsa",
            },
        )
        # Response should contain human pathway identifiers
        assert "hsa" in str(result_text.content[0].text)


async def test_query_kegg_get_pathway_data():
    """Test the tool query_kegg for getting pathway data."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.GET,
                "entries": ["hsa00010"],
            },
        )
        # Response should contain pathway data
        assert "Glycolysis" in str(result_text.content[0].text)


async def test_query_kegg_get_gene_data():
    """Test the tool query_kegg for getting gene data."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.GET,
                "entries": ["hsa:7157"],  # TP53
            },
        )
        # Response should contain gene data
        assert "TP53" in str(result_text.content[0].text)


async def test_query_kegg_get_gene_sequence():
    """Test the tool query_kegg for getting gene sequence data."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.GET,
                "entries": ["hsa:7157"],  # TP53
                "option": KeggOption.AASEQ,
            },
        )
        # Response should contain amino acid sequence
        assert "MEEPQ" in str(result_text.data)


async def test_query_kegg_find_compounds():
    """Test the tool query_kegg for finding compounds by formula."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.FIND,
                "database": KeggDatabase.COMPOUND,
                "query": "C7H10O5",
                "option": "formula",
            },
        )
        # Response should contain compound data
        assert "C7H10O5" in str(result_text.data)


async def test_query_kegg_link_pathway_genes():
    """Test the tool query_kegg for linking pathway to genes."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.LINK,
                "target_db": "genes",
                "source_db": "hsa:00010",  # Glycolysis pathway
            },
        )
        # Response should contain gene links
        assert "hsa:" in str(result_text.data)


async def test_query_kegg_conv():
    """Test the tool query_kegg for converting between database identifiers."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.CONV,
                "target_db": "ncbi-geneid",
                "source_db": "hsa:7157",  # TP53
            },
        )
        # Response should contain the NCBI Gene ID for TP53
        assert "7157" in str(result_text.data)


async def test_query_kegg_info():
    """Test the tool query_kegg for retrieving database information."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.INFO,
                "database": KeggDatabase.PATHWAY,
            },
        )
        # Response should contain pathway database information
        assert "pathway" in str(result_text.data)


async def test_query_kegg_invalid_operation():
    """Test the tool query_kegg with an invalid operation."""
    async with Client(core_mcp) as client:
        with pytest.raises(ToolError):
            await client.call_tool(
                "query_kegg",
                {
                    "operation": "INVALID_OPERATION",  # Invalid operation
                    "database": KeggDatabase.PATHWAY,
                },
            )


async def test_workflow_get_id_then_query():
    """Test a complete workflow: get KEGG ID by gene symbol then query data about the gene."""
    async with Client(core_mcp) as client:
        # First, get the KEGG ID
        kegg_id_result = await client.call_tool(
            "get_kegg_id_by_gene_symbol", {"gene_symbol": "TP53", "organism_code": "9606"}
        )
        # Split the result at the tab character to get the KEGG ID
        kegg_id = kegg_id_result.content[0].text.split("\t")[-1].strip()

        # Verify we got a valid KEGG ID
        assert kegg_id == "hsa:7157", f"Expected KEGG ID for TP53 not found, got: {kegg_id}"

        # Next, query gene data using the KEGG ID
        gene_data_result = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.GET,
                "entries": [kegg_id],
            },
        )

        # Then, find pathways related to this gene
        pathway_result = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.LINK,
                "target_db": KeggDatabase.PATHWAY,
                "entries": [kegg_id],
            },
        )

        # Verify the results
        assert "TP53" in str(gene_data_result.content[0].text)
        assert "path:hsa" in str(pathway_result.content[0].text)


async def test_query_kegg_get_pathway_by_query():
    """Test the tool query_kegg for getting pathway information using direct query."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.GET,
                "entries": ["hsa00010"],
            },
        )
        # Response should contain glycolysis pathway data
        assert "Glycolysis" in str(result_text.data)


async def test_query_kegg_find_compound_caffeine():
    """Test the tool query_kegg for finding the compound ID for caffeine."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.FIND,
                "database": KeggDatabase.COMPOUND,
                "query": "caffeine",
            },
        )
        # Response should contain caffeine compound information
        assert "caffeine" in str(result_text.data).lower()
        assert "cpd:C07481" in str(result_text.data)


async def test_query_kegg_find_drug_acetaminophen():
    """Test the tool query_kegg for finding the drug ID for acetaminophen."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.FIND,
                "database": KeggDatabase.DRUG,
                "query": "acetaminophen",
            },
        )
        # Response should contain acetaminophen drug information
        assert "acetaminophen" in str(result_text.data).lower()
        assert "dr:D00217" in str(result_text.data)


async def test_query_kegg_drug_drug_interaction():
    """Test the tool query_kegg for checking drug-drug interactions between ibuprofen and aspirin."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "query_kegg",
            {
                "operation": KeggOperation.DDI,
                "entries": ["dr:D00126", "dr:D00109"],  # ibuprofen and aspirin
            },
        )
        # Response should contain interaction information
        response_text = str(result_text.data)
        assert "D00126" in response_text
        assert "D00109" in response_text
        # The response should contain interaction details on Cyclooxygenase-1 (PTGS1)
        assert "PTGS1" in response_text
