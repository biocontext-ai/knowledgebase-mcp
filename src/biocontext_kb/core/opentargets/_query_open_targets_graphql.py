from typing import Annotated, Optional

from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.utils import execute_graphql_query


@core_mcp.tool()
def query_open_targets_graphql(
    query_string: Annotated[str, Field(description="GraphQL query string starting with 'query' keyword")],
    variables: Annotated[Optional[dict], Field(description="Optional variables for the GraphQL query")] = None,
) -> dict:
    """Execute GraphQL queries against the Open Targets API. Use get_open_targets_query_examples() or get_open_targets_graphql_schema() first.

    Returns:
        dict: GraphQL response with data field containing targets, diseases, drugs, variants, studies or error message.
    """
    base_url = "https://api.platform.opentargets.org/api/v4/graphql"
    try:
        response = execute_graphql_query(base_url, query_string, variables)
        return response
    except Exception as e:
        return {"error": f"Failed to execute GraphQL query: {e!s}"}
