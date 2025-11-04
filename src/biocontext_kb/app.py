import asyncio
import logging
import os

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from biocontext_kb.core import core_mcp
from biocontext_kb.openapi import get_openapi_mcps
from biocontext_kb.utils import slugify

logger = logging.getLogger(__name__)


async def get_mcp_tools(mcp_app: FastMCP):
    """Check the MCP server for the number of tools, resources, and templates."""
    tools = await mcp_app.get_tools()
    resources = await mcp_app.get_resources()
    templates = await mcp_app.get_resource_templates()

    logger.info(f"{mcp_app.name} - {len(tools)} Tool(s): {', '.join([t.name for t in tools.values()])}")
    logger.info(
        f"{mcp_app.name} - {len(resources)} Resource(s): {', '.join([(r.name if r.name is not None else '') for r in resources.values()])}"
    )
    logger.info(
        f"{mcp_app.name} - {len(templates)} Resource Template(s): {', '.join([t.name for t in templates.values()])}"
    )


async def setup(mcp_app: FastMCP):
    """Setup function to initialize the MCP server."""
    logger.info("Environment: %s", os.environ.get("MCP_ENVIRONMENT"))

    logger.info("Setting up MCP server...")
    for mcp in [core_mcp, *(await get_openapi_mcps())]:
        await mcp_app.import_server(
            mcp,
            slugify(mcp.name),
        )
    logger.info("MCP server setup complete.")

    logger.info("Checking MCP server for valid tools...")
    await get_mcp_tools(mcp_app)
    logger.info("MCP server tools check complete.")

    logger.info("Starting MCP server...")
    if os.environ.get("MCP_ENVIRONMENT") == "PRODUCTION":
        # Get the StreamableHTTP app from the MCP server
        app = mcp_app.http_app(path="/mcp/", stateless_http=True)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Be more restrictive in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        return app
    else:
        return mcp_app


mcp_app: FastMCP = FastMCP(
    name="BioContextAI",
    instructions="Provides access to biomedical knowledge bases.",
    on_duplicate_tools="error",
)

app = asyncio.run(setup(mcp_app))
