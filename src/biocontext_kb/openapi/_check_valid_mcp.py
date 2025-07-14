import logging

from fastmcp.server.openapi import FastMCPOpenAPI

from biocontext_kb.utils import slugify

logger = logging.getLogger(__name__)


async def check_valid_mcp(mcp: FastMCPOpenAPI) -> bool:
    """Check that all tools and resources are alphanumeric and at most 64 characters.

    Args:
        mcp (FastMCPOpenAPI): The OpenAPI-based MCP.

    Returns:
        bool: Whether the MCP server is valid.
    """
    tools = await mcp.get_tools()
    resources = await mcp.get_resources()
    templates = await mcp.get_resource_templates()

    prefix_length = len(slugify(mcp.name)) + 1

    keys = [*tools.keys(), *resources.keys(), *templates.keys()]
    if not keys:
        logger.error(f"No tools, resources, or templates found in MCP server {mcp.name}.")
        return False

    def is_valid_name(name: str) -> bool:
        """Check if the name is alphanumeric or contains only valid characters (a-z, A-Z, 0-9, _, -)."""
        return all(c.isalnum() or c in ["_", "-"] for c in name)

    for name in keys:
        if not is_valid_name(name) or (len(name) + prefix_length) > 64:
            logger.error(f"Invalid name `{name}` in MCP server {mcp.name}.")
            return False

    return True
