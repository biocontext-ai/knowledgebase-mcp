from graphql import print_schema

from biocontext_kb.core._server import core_mcp
from biocontext_kb.utils import fetch_graphql_schema


@core_mcp.tool()
def get_open_targets_graphql_schema() -> dict:
    """Fetch the Open Targets GraphQL schema."""
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"
    try:
        schema = fetch_graphql_schema(base_url)
        return {"schema": print_schema(schema)}
    except Exception as e:
        return {"error": f"Failed to fetch Open Targets GraphQL schema: {e!s}"}
