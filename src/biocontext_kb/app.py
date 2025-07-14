import asyncio
import logging
import os

from fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware

from biocontext_kb.core import core_mcp
from biocontext_kb.openapi import get_openapi_mcps
from biocontext_kb.utils import slugify

logger = logging.getLogger(__name__)


class MCPPathRewriteMiddleware:
    """Middleware to rewrite the path for MCP server in production mode.

    This is necessary as some MCP clients expect the path to be /mcp, but the FastMCP server
    serves the app at /mcp/ by default. This middleware rewrites the path to ensure
    compatibility with such clients.

    Based on: https://github.com/jlowin/fastmcp/issues/991#issuecomment-3045939301
    """

    def __init__(self, app):
        """Initialize the middleware with the Starlette app."""
        self.app = app

    async def __call__(self, scope, receive, send):
        """Rewrite the path for the MCP server."""
        if scope["type"] == "http" and scope.get("path") == "/mcp":
            # Rewrite /mcp to /mcp/ at ASGI level
            new_scope = dict(scope)
            new_scope["path"] = "/mcp/"
            new_scope["raw_path"] = b"/mcp/"
            return await self.app(new_scope, receive, send)
        return await self.app(scope, receive, send)


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
        mcp_app_http = mcp_app.http_app(path="/mcp", stateless_http=True)
        mcp_app_http.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Be more restrictive in production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app = MCPPathRewriteMiddleware(mcp_app_http)

        return app
    else:
        return mcp_app


mcp_app: FastMCP = FastMCP(
    name="BioContextAI",
    instructions="Provides access to biomedical knowledge bases.",
    on_duplicate_tools="error",
)

app = asyncio.run(setup(mcp_app))
