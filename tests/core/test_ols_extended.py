import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_available_ontologies():
    """Test the tool get_available_ontologies."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_available_ontologies", {})
        result = result_raw.data
        assert result.get("ontologies")
        assert len(result["ontologies"]) > 0
        assert result.get("total_ontologies") > 0
        # Check that the first result has expected structure
        first_ontology = result["ontologies"][0]
        assert "id" in first_ontology
        assert "name" in first_ontology
        # Should include common ontologies
        ontology_ids = [ont["id"] for ont in result["ontologies"]]
        assert "efo" in ontology_ids
        assert "go" in ontology_ids


async def test_get_go_terms_by_gene():
    """Test the tool get_go_terms_by_gene."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_go_terms_by_gene", {"gene_name": "TP53"})
        result = result_raw.data
        assert result.get("go_terms")
        assert len(result["go_terms"]) > 0
        # Check that the first result has expected structure
        first_result = result["go_terms"][0]
        assert "id" in first_result
        assert "label" in first_result
        assert first_result["id"].startswith("GO_")


async def test_get_hpo_terms_by_phenotype():
    """Test HPO terms using the general search function."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool(
            "search_ontology_terms", {"search_term": "seizures", "ontologies": "hp", "size": 5}
        )
        result = result_raw.data
        assert result.get("terms")
        if result["terms"]:
            # Check that we get HP terms
            hp_terms = [term for term in result["terms"] if term.get("curie", "").startswith("HP:")]
            assert len(hp_terms) > 0
            first_result = hp_terms[0]
            assert "id" in first_result
            assert "label" in first_result


async def test_get_chebi_terms_by_chemical():
    """Test the tool get_chebi_terms_by_chemical."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_chebi_terms_by_chemical", {"chemical_name": "glucose"})
        result = result_raw.data
        assert result.get("chebi_terms")
        assert len(result["chebi_terms"]) > 0
        # Check that the first result has expected structure
        first_result = result["chebi_terms"][0]
        assert "id" in first_result
        assert "label" in first_result
        assert first_result["id"].startswith("CHEBI_")


async def test_get_uberon_terms_by_anatomy():
    """Test UBERON terms using the general search function."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool(
            "search_ontology_terms", {"search_term": "brain", "ontologies": "uberon", "size": 5}
        )
        result = result_raw.data
        assert result.get("terms")
        if result["terms"]:
            # Check that we get UBERON terms
            uberon_terms = [term for term in result["terms"] if term.get("curie", "").startswith("UBERON:")]
            assert len(uberon_terms) > 0
            first_result = uberon_terms[0]
            assert "id" in first_result
            assert "label" in first_result


async def test_get_cell_ontology_terms():
    """Test the tool get_cell_ontology_terms."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_cell_ontology_terms", {"cell_type": "T cell"})
        result = result_raw.data
        assert result.get("cl_terms")
        assert len(result["cl_terms"]) > 0
        # Check that the first result has expected structure
        first_result = result["cl_terms"][0]
        assert "id" in first_result
        assert "label" in first_result
        assert first_result["id"].startswith("CL_")


async def test_search_ontology_terms():
    """Test the tool search_ontology_terms."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool(
            "search_ontology_terms", {"search_term": "cancer", "ontologies": "efo,mondo", "size": 5}
        )
        result = result_raw.data
        assert result.get("terms")
        assert len(result["terms"]) > 0
        assert result.get("terms_by_ontology")
        assert result.get("total_results") > 0
        assert result.get("ontologies_found")


async def test_search_ontology_terms_all():
    """Test the tool search_ontology_terms across all ontologies."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("search_ontology_terms", {"search_term": "apoptosis", "size": 10})
        result = result_raw.data
        assert result.get("terms")
        assert len(result["terms"]) > 0
        assert result.get("terms_by_ontology")


async def test_get_term_details():
    """Test the tool get_term_details."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool("get_term_details", {"term_id": "EFO:0000001", "ontology_id": "efo"})
        result = result_raw.data
        if "error" not in result:
            assert result.get("term_details")
            term_details = result["term_details"]
            assert "id" in term_details
            assert "label" in term_details
            assert "curie" in term_details


async def test_get_term_hierarchical_children():
    """Test the tool get_term_hierarchical_children."""
    async with Client(core_mcp) as client:
        result_raw = await client.call_tool(
            "get_term_hierarchical_children",
            {
                "term_id": "EFO:0000408",  # disease
                "ontology_id": "efo",
                "size": 5,
            },
        )
        result = result_raw.data
        if "error" not in result:
            assert result.get("hierarchical_children")
            assert result.get("parent_term") == "EFO:0000408"
            if result["hierarchical_children"]:
                first_child = result["hierarchical_children"][0]
                assert "id" in first_child
                assert "label" in first_child


# Test error conditions
async def test_get_go_terms_by_gene_empty():
    """Test the tool get_go_terms_by_gene with empty gene name."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_go_terms_by_gene", {"gene_name": ""})
        assert "error" in result.content[0].text
        assert "gene_name must be provided" in result.content[0].text


async def test_search_ontology_terms_empty():
    """Test the tool search_ontology_terms with empty search term."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("search_ontology_terms", {"search_term": ""})
        assert "error" in result.content[0].text
        assert "search_term must be provided" in result.content[0].text
