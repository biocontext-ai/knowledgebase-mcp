from typing import Dict, List

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.panglaodb._get_panglaodb_df import get_panglaodb_df


@core_mcp.tool()
def get_panglaodb_options() -> Dict[str, List[str] | str]:
    """Retrieves the available options for filtering marker genes in the PanglaoDB dataset.

    Returns:
        A dictionary containing lists of unique values for species, organ, cell type, and gene symbols.
    """
    panglao_db_df = get_panglaodb_df()
    if panglao_db_df is None:
        return {"error": "PanglaoDB data is not loaded. Check server logs."}

    # Get unique values for each column, handling NaN values
    organ = panglao_db_df["organ"].dropna().str.lower().unique().tolist()
    cell_type = panglao_db_df["cell type"].dropna().str.lower().unique().tolist()

    return {
        "organ": organ,
        "cell_type": cell_type,
    }
