from typing import Annotated, Any, Dict, Optional

from pydantic import Field

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.panglaodb._get_panglaodb_df import get_panglaodb_df


@core_mcp.tool()
def get_panglaodb_marker_genes(
    species: Annotated[str, Field(description="The species ('Hs' for Human or 'Mm' for Mouse)")],
    min_sensitivity: Annotated[
        Optional[float],
        Field(
            description="Minimum sensitivity score (0-1). Applied to species-specific column.",
            ge=0,
            le=1,
        ),
    ] = None,
    min_specificity: Annotated[
        Optional[float],
        Field(
            description="Minimum specificity score (0-1). Applied to species-specific column.",
            ge=0,
            le=1,
        ),
    ] = None,
    organ: Annotated[
        Optional[str],
        Field(description="Filter by organ (e.g., 'Brain', 'Lung'). Case-insensitive."),
    ] = None,
    cell_type: Annotated[
        Optional[str],
        Field(description="Filter by cell type (e.g., 'Smooth muscle cells', 'T cells'). Case-insensitive."),
    ] = None,
    gene_symbol: Annotated[
        Optional[str],
        Field(description="Filter by gene symbol (e.g., 'MAFB', 'SYNPO'). Case-insensitive."),
    ] = None,
) -> Dict[str, Any]:
    """Retrieves marker genes from the PanglaoDB dataset based on specified filters.

    Args:
        species: The species ('Hs' for Human or 'Mm' for Mouse).
        min_sensitivity: Minimum sensitivity score (0-1).
        min_specificity: Minimum specificity score (0-1).
        organ: Filter by organ name (case-insensitive).
        cell_type: Filter by cell type name (case-insensitive).
        gene_symbol: Filter by gene symbol (case-insensitive).

    Returns:
        A dictionary containing a list of matching marker gene records or an error message.
    """
    panglao_db_df = get_panglaodb_df()
    if panglao_db_df is None:
        return {"error": "PanglaoDB data is not loaded. Check server logs."}

    # Make a copy to avoid modifying the original DataFrame
    filtered_df = panglao_db_df.copy()

    # Filter by species - properly handle NaN values
    if species == "Hs":
        filtered_df = filtered_df[filtered_df["species"].fillna("").str.contains("Hs", na=False)]
        sensitivity_col = "sensitivity_human"
        specificity_col = "specificity_human"
    elif species == "Mm":
        filtered_df = filtered_df[filtered_df["species"].fillna("").str.contains("Mm", na=False)]
        sensitivity_col = "sensitivity_mouse"
        specificity_col = "specificity_mouse"
    else:
        return {"error": "Invalid species. Use 'Hs' for Human or 'Mm' for Mouse."}

    # Filter by minimum sensitivity with NaN handling
    if min_sensitivity is not None:
        # Convert NaN values to appropriate defaults (e.g., 0)
        filtered_df = filtered_df[filtered_df[sensitivity_col].fillna(0) >= min_sensitivity]

    # Filter by minimum specificity with NaN handling
    if min_specificity is not None:
        filtered_df = filtered_df[filtered_df[specificity_col].fillna(0) >= min_specificity]

    # Filter by organ (case-insensitive)
    if organ is not None:
        filtered_df = filtered_df[filtered_df["organ"].fillna("").str.lower().str.contains(organ.lower(), na=False)]

    # Filter by cell type (case-insensitive)
    if cell_type is not None:
        filtered_df = filtered_df[
            filtered_df["cell type"].fillna("").str.lower().str.contains(cell_type.lower(), na=False)
        ]

    # Filter by gene symbols (case-insensitive)
    if gene_symbol is not None:
        filtered_df = filtered_df[
            filtered_df["official gene symbol"].fillna("").str.contains(gene_symbol, case=False, na=False)
        ]

    # Convert the filtered DataFrame to a list of dictionaries
    result = filtered_df.to_dict(orient="records")

    return {"markers": result}
