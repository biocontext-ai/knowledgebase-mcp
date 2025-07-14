import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_open_targets_graphql_schema():
    """Test the tool get_open_targets_graphql_schema."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_open_targets_graphql_schema", {})
        result = json.loads(result_text.content[0].text)

        # Verify we get a schema back
        assert "schema" in result


async def test_get_open_targets_query_examples():
    """Test the tool get_open_targets_query_examples."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_open_targets_query_examples", {})
        result = json.loads(result_text.content[0].text)

        # Verify we get example queries back
        assert "informationForTargetByEnsemblId" in result
        assert "associatedDiseasesForTargetByEnsemblId" in result
        assert "informationForDiseaseByEFOId" in result
        assert "knownDrugsForDiseaseByEFOId" in result
        assert "associatedTargetsForDiseaseByEFOId" in result


async def test_query_open_targets_graphql_target_annotation():
    """Test the tool query_open_targets_graphql with target annotation query."""
    async with Client(core_mcp) as client:
        # First get the example queries
        examples_text = await client.call_tool("get_open_targets_query_examples", {})
        examples = examples_text.data

        # Use the informationForTargetByEnsemblId example query
        query = examples["informationForTargetByEnsemblId"]

        # Execute the query
        result_text = await client.call_tool("query_open_targets_graphql", {"query_string": query, "variables": {}})
        result = result_text.data

        # Verify response structure
        assert "status" in result
        assert result["status"] == "success"
        assert "data" in result
        assert "target" in result["data"]

        # Check specific data
        target_data = result["data"]["target"]
        assert target_data["approvedSymbol"] is not None
        assert "tractability" in target_data


async def test_query_open_targets_graphql_disease_targets():
    """Test the tool query_open_targets_graphql with disease-target associations query."""
    async with Client(core_mcp) as client:
        # First get the example queries
        examples_text = await client.call_tool("get_open_targets_query_examples", {})
        examples = examples_text.data

        # Use the associatedDiseasesForTargetByEnsemblId example query
        query = examples["associatedDiseasesForTargetByEnsemblId"]

        # Execute the query
        result_text = await client.call_tool("query_open_targets_graphql", {"query_string": query, "variables": {}})
        result = json.loads(result_text.content[0].text)

        # Verify response structure
        assert "status" in result
        assert result["status"] == "success"
        assert "data" in result
        assert "associatedDiseases" in result["data"]["target"].keys()


async def test_query_open_targets_graphql_invalid_query():
    """Test the tool query_open_targets_graphql with an invalid GraphQL query."""
    async with Client(core_mcp) as client:
        invalid_query = """
            query invalidQuery {
                nonExistentField {
                    id
                    name
                }
            }
        """

        result_text = await client.call_tool(
            "query_open_targets_graphql", {"query_string": invalid_query, "variables": {}}
        )
        result = json.loads(result_text.content[0].text)

        # Should return an error status
        assert "status" in result
        assert result["status"] == "error"


async def test_query_open_targets_graphql_with_variables():
    """Test the tool query_open_targets_graphql with query variables."""
    async with Client(core_mcp) as client:
        # Custom query with variables for TP53
        query = """
            query targetById($ensemblId: String!) {
                target(ensemblId: $ensemblId) {
                    id
                    approvedSymbol
                    approvedName
                }
            }
        """

        variables = {"ensemblId": "ENSG00000141510"}  # TP53

        result_text = await client.call_tool(
            "query_open_targets_graphql", {"query_string": query, "variables": variables}
        )
        result = json.loads(result_text.content[0].text)

        # Verify response structure
        assert "status" in result
        assert result["status"] == "success"
        assert "data" in result
        assert "target" in result["data"]

        # Check specific data for TP53
        target_data = result["data"]["target"]
        assert target_data["approvedSymbol"] == "TP53"
