from pathlib import Path

import pandas as pd


def get_panglaodb_df() -> pd.DataFrame | None:
    """Load the PanglaoDB dataset into a pandas DataFrame.

    Returns:
        pd.DataFrame | None: The loaded DataFrame or None if loading fails.
    """
    # Construct the path to the TSV file
    panglao_db_path = Path(__file__).parent / "data" / "PanglaoDB_markers_27_Mar_2020.tsv"

    # Load the database into a pandas DataFrame
    try:
        panglao_db_df = pd.read_csv(panglao_db_path, sep="\t", engine="python", header=0)
        # Replace empty strings and other potential non-values with NaN for consistency
        panglao_db_df = panglao_db_df.replace("", pd.NA)
        return panglao_db_df
    except FileNotFoundError:
        print(f"Error: PanglaoDB file not found at {panglao_db_path}")
        return None
    except Exception as e:
        print(f"Error loading PanglaoDB file: {e}")
        return None
