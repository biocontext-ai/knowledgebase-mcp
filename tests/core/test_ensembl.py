import pytest  # noqa: F401
import pytest_asyncio  # noqa: F401
from fastmcp import Client

from biocontext_kb.core._server import core_mcp


async def test_get_ensembl_id_from_gene_symbol():
    """Test the tool get_ensembl_id_from_gene_symbol."""
    async with Client(core_mcp) as client:
        result = await client.call_tool("get_ensembl_id_from_gene_symbol", {"gene_symbol": "TP53"})
        assert "ENSG00000141510" in result.content[0].text
