import json

import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_search_studies_by_condition():
    """Test the search_studies tool with a condition parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_studies", {"condition": "diabetes"})
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert isinstance(result["studies"], list)
        assert len(result["studies"]) > 0

        # Check for expected fields in the first study
        first_study = result["studies"][0]
        assert "protocolSection" in first_study
        assert "nctId" in first_study["protocolSection"]["identificationModule"]


async def test_search_studies_by_intervention():
    """Test the search_studies tool with an intervention parameter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_studies", {"intervention": "aspirin"})
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert isinstance(result["studies"], list)
        assert len(result["studies"]) > 0


async def test_search_studies_multiple_params():
    """Test the search_studies tool with multiple parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "search_studies",
            {"condition": "cancer", "status": "RECRUITING", "study_type": "INTERVENTIONAL", "page_size": 10},
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert isinstance(result["studies"], list)
        assert len(result["studies"]) <= 10  # Should respect page_size


async def test_search_studies_no_params():
    """Test the search_studies tool with no parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_studies", {})
        result = json.loads(result_text.content[0].text)

        # Should return an error
        assert "error" in result


async def test_get_study_details_valid_nct():
    """Test the get_study_details tool with a valid NCT ID."""
    async with Client(core_mcp) as client:
        # First, get a valid NCT ID from a search
        search_result_text = await client.call_tool("search_studies", {"condition": "diabetes", "page_size": 1})
        search_result = search_result_text.data

        if "studies" in search_result and len(search_result["studies"]) > 0:
            nct_id = search_result["studies"][0]["protocolSection"]["identificationModule"]["nctId"]

            # Now get details for this study
            result_text = await client.call_tool("get_study_details", {"nct_id": nct_id})
            result = json.loads(result_text.content[0].text)

            # Verify we get study details
            assert "protocolSection" in result
            assert "identificationModule" in result["protocolSection"]
            assert result["protocolSection"]["identificationModule"]["nctId"] == nct_id
        else:
            # If no studies found, test with a known NCT ID format
            result = (await client.call_tool("get_study_details", {"nct_id": "NCT00000102"})).data
            # Either get results or an error (but not a validation error)
            assert isinstance(result, dict)


async def test_get_study_details_invalid_nct():
    """Test the get_study_details tool with an invalid NCT ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_study_details", {"nct_id": "NCT99999999"})
        result = json.loads(result_text.content[0].text)

        # Should return an error
        assert "error" in result


async def test_get_study_details_malformed_nct():
    """Test the get_study_details tool with a malformed NCT ID."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_study_details", {"nct_id": "INVALID123"})
        result = json.loads(result_text.content[0].text)

        # Should return an error
        assert "error" in result
        assert "Invalid NCT ID format" in result["error"]


async def test_get_studies_by_condition():
    """Test the get_studies_by_condition tool."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_studies_by_condition", {"condition": "breast cancer"})
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back with summary
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)
        assert len(result["studies"]) > 0

        # Check summary fields
        summary = result["summary"]
        assert "condition_searched" in summary
        assert summary["condition_searched"] == "breast cancer"
        assert "total_studies" in summary
        assert "status_breakdown" in summary
        assert "study_type_breakdown" in summary


async def test_get_studies_by_condition_with_filters():
    """Test the get_studies_by_condition tool with additional filters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_studies_by_condition",
            {
                "condition": "diabetes",
                "status": "RECRUITING",
                "study_type": "INTERVENTIONAL",
                "location_country": "United States",
            },
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)


async def test_get_studies_by_intervention():
    """Test the get_studies_by_intervention tool."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_studies_by_intervention", {"intervention": "metformin"})
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back with summary
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)

        # Check summary fields
        summary = result["summary"]
        assert "intervention_searched" in summary
        assert summary["intervention_searched"] == "metformin"
        assert "total_studies" in summary
        assert "status_breakdown" in summary
        assert "phase_breakdown" in summary
        assert "top_conditions" in summary
        assert "top_sponsors" in summary


async def test_get_studies_by_intervention_with_condition():
    """Test the get_studies_by_intervention tool with condition filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_studies_by_intervention", {"intervention": "insulin", "condition": "diabetes", "phase": "PHASE3"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)


async def test_get_recruiting_studies_by_location():
    """Test the get_recruiting_studies_by_location tool."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_recruiting_studies_by_location", {"location_country": "United States"}
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back with summary
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)

        # Check summary fields
        summary = result["summary"]
        assert "search_location" in summary
        assert summary["search_location"]["country"] == "United States"
        assert "total_recruiting_studies" in summary
        assert "study_type_breakdown" in summary
        assert "recruiting_locations" in summary


async def test_get_recruiting_studies_by_location_with_state():
    """Test the get_recruiting_studies_by_location tool with state filter."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool(
            "get_recruiting_studies_by_location",
            {"location_country": "United States", "location_state": "California", "condition": "cancer"},
        )
        result = json.loads(result_text.content[0].text)

        # Verify we get studies back
        assert "studies" in result
        assert "summary" in result
        assert isinstance(result["studies"], list)


async def test_get_recruiting_studies_by_location_no_country():
    """Test the get_recruiting_studies_by_location tool without country."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool("get_recruiting_studies_by_location", {})
            # If we get here, the call succeeded but shouldn't have
            raise AssertionError("Expected tool to fail validation")
        except Exception as e:
            # Should get a validation error for missing required parameter
            assert "Missing required argument" in str(e) or "location_country" in str(e)


async def test_get_studies_by_condition_no_condition():
    """Test the get_studies_by_condition tool without condition."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool("get_studies_by_condition", {})
            # If we get here, the call succeeded but shouldn't have
            raise AssertionError("Expected tool to fail validation")
        except Exception as e:
            # Should get a validation error for missing required parameter
            assert "Missing required argument" in str(e) or "condition" in str(e)


async def test_get_studies_by_intervention_no_intervention():
    """Test the get_studies_by_intervention tool without intervention."""
    async with Client(core_mcp) as client:
        try:
            await client.call_tool("get_studies_by_intervention", {})
            # If we get here, the call succeeded but shouldn't have
            raise AssertionError("Expected tool to fail validation")
        except Exception as e:
            # Should get a validation error for missing required parameter
            assert "Missing required argument" in str(e) or "intervention" in str(e)
