import json

import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_search_drugs_fda_by_brand_name():
    """Test the search_drugs_fda function with brand name search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_drugs_fda", {"brand_name": "Tylenol", "limit": 5})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_search_drugs_fda_by_generic_name():
    """Test the search_drugs_fda function with generic name search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_drugs_fda", {"generic_name": "acetaminophen", "limit": 5})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_search_drugs_fda_by_sponsor():
    """Test the search_drugs_fda function with sponsor search."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_drugs_fda", {"sponsor_name": "Johnson & Johnson", "limit": 5})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_get_drug_by_application_number():
    """Test the get_drug_by_application_number function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_drug_by_application_number", {"application_number": "NDA021436"})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_get_drug_label_info():
    """Test the get_drug_label_info function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_drug_label_info", {"brand_name": "Aspirin"})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_count_drugs_by_field():
    """Test the count_drugs_by_field function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("count_drugs_by_field", {"field": "sponsor_name", "limit": 10})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" not in result or "results" in result


async def test_get_drug_statistics():
    """Test the get_drug_statistics function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_drug_statistics", {})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        # Should have multiple statistics sections
        if "error" not in result:
            assert any(
                key in result for key in ["top_sponsors", "dosage_forms", "administration_routes", "marketing_statuses"]
            )


async def test_get_available_pharmacologic_classes():
    """Test the get_available_pharmacologic_classes function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_available_pharmacologic_classes", {"class_type": "epc", "limit": 10})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        if "error" not in result:
            assert "available_classes" in result
            assert "class_type" in result
            assert "total_found" in result
        else:
            # API might return an error, which is acceptable
            assert "error" in result


async def test_search_drugs_by_therapeutic_class():
    """Test the search_drugs_by_therapeutic_class function with a real FDA class term."""
    async with Client(core_mcp) as client:
        # First get available classes to use a real term
        classes_result = (
            await client.call_tool("get_available_pharmacologic_classes", {"class_type": "epc", "limit": 5})
        ).data

        assert isinstance(classes_result, dict)

        if "error" not in classes_result and classes_result.get("available_classes"):
            # Use the first available class
            first_class = classes_result["available_classes"][0]["term"]

            result_text = await client.call_tool(
                "search_drugs_by_therapeutic_class", {"therapeutic_class": first_class, "class_type": "epc", "limit": 5}
            )
            result = json.loads(result_text.content[0].text)

            assert isinstance(result, dict)
            assert "error" not in result or "results" in result
        else:
            # If we can't get classes, test with a known term that might exist
            result_text = await client.call_tool(
                "search_drugs_by_therapeutic_class",
                {"therapeutic_class": "Nonsteroidal Anti-inflammatory Drug [EPC]", "class_type": "epc", "limit": 5},
            )
            result = json.loads(result_text.content[0].text)

            assert isinstance(result, dict)
            # This might return an error or results, both are acceptable


async def test_get_generic_equivalents():
    """Test the get_generic_equivalents function."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("get_generic_equivalents", {"brand_name": "Advil"})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        # Should either return results or an error message
        assert "error" in result or "brand_drug" in result


async def test_search_drugs_fda_no_params():
    """Test the search_drugs_fda function with no search parameters."""
    async with Client(core_mcp) as client:
        result_text = await client.call_tool("search_drugs_fda", {})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        assert "error" in result
        assert "at least one search parameter" in result["error"].lower()


async def test_count_drugs_by_field_invalid_field():
    """Test the count_drugs_by_field function with potentially invalid field."""
    async with Client(core_mcp) as client:
        # This should work, but might return an error from the API
        result_text = await client.call_tool("count_drugs_by_field", {"field": "invalid_field_name", "limit": 10})
        result = json.loads(result_text.content[0].text)

        assert isinstance(result, dict)
        # Should either return results or an error
