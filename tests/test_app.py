import importlib
import logging  # Added logging import
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import FastMCP
from fastmcp.server.openapi import FastMCPOpenAPI

from biocontext_kb.app import get_mcp_tools, setup
from biocontext_kb.core import core_mcp
from biocontext_kb.utils import slugify


@pytest.fixture
def mock_mcp_app():
    """Create a mock FastMCP instance for testing."""
    mock_app = MagicMock(spec=FastMCP)
    mock_app.name = "Test MCP App"

    # Create proper mocks for tools with string names
    tool_mock = MagicMock()
    tool_mock.name = "test_tool"
    mock_app.get_tools = AsyncMock(return_value={"test_tool": tool_mock})

    # Create a resource mock with name attribute set to None to match the application behavior
    resource_mock = MagicMock()
    resource_mock.name = None
    mock_app.get_resources = AsyncMock(return_value={"test_resource": resource_mock})

    # Create template mock with string name
    template_mock = MagicMock()
    template_mock.name = "test_template"
    mock_app.get_resource_templates = AsyncMock(return_value={"test_template": template_mock})

    mock_app.import_server = AsyncMock()
    mock_app.http_app = MagicMock(return_value=MagicMock())
    return mock_app


@pytest.mark.asyncio
async def test_get_mcp_tools(mock_mcp_app, caplog):
    """Test that get_mcp_tools logs the correct information."""
    with caplog.at_level(logging.INFO):
        await get_mcp_tools(mock_mcp_app)

    # Check that the appropriate log messages were created
    assert "Test MCP App - 1 Tool(s): test_tool" in caplog.text
    assert "Test MCP App - 1 Resource(s): " in caplog.text
    assert "Test MCP App - 1 Resource Template(s): test_template" in caplog.text

    # Verify the mock functions were called
    mock_mcp_app.get_tools.assert_called_once()
    mock_mcp_app.get_resources.assert_called_once()
    mock_mcp_app.get_resource_templates.assert_called_once()


@pytest.mark.asyncio
async def test_setup_development_environment(mock_mcp_app, monkeypatch):
    """Test setup function in development environment."""
    monkeypatch.setenv("MCP_ENVIRONMENT", "DEVELOPMENT")

    mock_openapi_mcps = [MagicMock(spec=FastMCPOpenAPI, name="openapi_mcp")]

    with patch("biocontext_kb.app.get_openapi_mcps", AsyncMock(return_value=mock_openapi_mcps)):
        result = await setup(mock_mcp_app)

    # Check that import_server was called for each MCP server
    assert mock_mcp_app.import_server.call_count == 2
    mock_mcp_app.import_server.assert_any_call(core_mcp, slugify(core_mcp.name))
    mock_mcp_app.import_server.assert_any_call(
        mock_openapi_mcps[0],
        slugify(mock_openapi_mcps[0].name),
    )

    # In development environment, the function should return the mcp_app directly
    assert result == mock_mcp_app


@pytest.mark.asyncio
async def test_setup_production_environment(mock_mcp_app, monkeypatch):
    """Test setup function in production environment."""
    monkeypatch.setenv("MCP_ENVIRONMENT", "PRODUCTION")

    mock_openapi_mcps = [MagicMock(spec=FastMCPOpenAPI, name="openapi_mcp")]
    mock_http_app = MagicMock()
    mock_mcp_app.http_app.return_value = mock_http_app

    with patch("biocontext_kb.app.get_openapi_mcps", AsyncMock(return_value=mock_openapi_mcps)):
        _result = await setup(mock_mcp_app)

    # Check that import_server was called for each MCP server
    assert mock_mcp_app.import_server.call_count == 2

    # Verify the Starlette app was created with the correct settings
    mock_mcp_app.http_app.assert_called_once_with(path="/mcp", stateless_http=True)


def test_app_initialization():
    """Test that the app is initialized correctly."""
    with patch("asyncio.run") as mock_run:
        # Import the app module to trigger the initialization code
        from biocontext_kb import app

        importlib.reload(app)

        # Verify that asyncio.run was called with setup function and a FastMCP instance
        mock_run.assert_called_once()
        args = mock_run.call_args[0]

        # First argument should be the awaitable from the setup function
        assert len(args) == 1

        coro = args[0]
        mcp_app_arg = coro.cr_frame.f_locals["mcp_app"]

        assert isinstance(mcp_app_arg, FastMCP)
        assert mcp_app_arg.name == "BioContextAI"
