import json
import logging
from pathlib import Path

import httpx
import requests
import yaml
from fastmcp.server.openapi import FastMCPOpenAPI, RouteMap, RouteType

from biocontext_kb.openapi._check_valid_mcp import check_valid_mcp

logger = logging.getLogger(__name__)


async def get_openapi_mcps() -> list[FastMCPOpenAPI]:
    """Get the OpenAPI MCPs."""
    schema_config_path = Path(__file__).parent / "config.yaml"
    if not schema_config_path.exists():
        raise FileNotFoundError(f"Config file {schema_config_path} not found.")

    schema_config = yaml.safe_load(schema_config_path.read_text(encoding="utf-8"))
    openapi_mcps: list[FastMCPOpenAPI] = []

    schemas = schema_config.get("schemas", [])
    if not schemas:
        logger.warning("No OpenAPI schemas found in the configuration.")
        return openapi_mcps

    for schema in schemas:
        # Download the OpenAPI schema from the URL if provided and parse it based on the type in the config
        try:
            schema_request = requests.get(schema["url"])
            schema_request.raise_for_status()

            if schema["type"] == "json":
                spec = json.loads(schema_request.text)
            elif schema["type"] == "yaml":
                spec = yaml.safe_load(schema_request.text)
            else:
                raise ValueError(f"Unsupported schema type: {schema['type']}")

        except requests.RequestException as e:
            logger.error(f"Failed to download schema from {schema['url']}: {e}")
            continue

        if (
            isinstance(spec.get("servers", False), list)
            and len(spec["servers"]) > 0
            and "url" in spec["servers"][0]
            and spec["servers"][0]["url"].startswith("http")
        ):
            # Use the first server URL as the base path
            base_path = spec["servers"][0]["url"]
        else:
            # Use the base path from the schema config
            base_path = schema.get("base", False)

        if not base_path:
            logger.error(f"Base path not found in schema: {schema['url']}")
            continue

        tool_mapping = [
            RouteMap(
                methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
                pattern=r".*",
                route_type=RouteType.TOOL,
            ),
        ]

        mcp = FastMCPOpenAPI(
            name=schema["name"],
            version=spec.get("info", {}).get("version", "1.0.0"),
            description=spec.get("info", {}).get("description", ""),
            openapi_spec=spec,
            client=httpx.AsyncClient(base_url=base_path),
            route_maps=tool_mapping,
        )

        if not await check_valid_mcp(mcp):
            continue

        openapi_mcps.append(mcp)

    return openapi_mcps
