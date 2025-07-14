import logging
import os

import click
import uvicorn


@click.command()
def run_app():
    """Main function to run the MCP server.

    If the environment variable MCP_ENVIRONMENT is set to PRODUCTION, it will run the Starlette app with streamable HTTP for the MCP server. Otherwise, it will run the MCP server via stdio.

    In production, the app will be mounted at /mcp/.
    The port is set via the PORT environment variable, defaulting to 8000 if not set.
    """
    logger = logging.getLogger(__name__)

    from biocontext_kb.app import MCPPathRewriteMiddleware, app

    if os.environ.get("MCP_ENVIRONMENT") == "PRODUCTION":
        logger.info("Starting Starlette app with Uvicorn in PRODUCTION mode.")
        uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
    elif not isinstance(app, MCPPathRewriteMiddleware):
        logger.info("Starting MCP server via stdio (non-PRODUCTION mode).")
        app.run(transport="stdio")
    else:
        logger.error("MCP server is not properly configured for non-PRODUCTION mode.")


if __name__ == "__main__":
    run_app()
