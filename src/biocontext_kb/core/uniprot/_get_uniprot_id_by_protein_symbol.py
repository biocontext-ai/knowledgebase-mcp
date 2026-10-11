from typing import Annotated, Any

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


def _search(query: str) -> list[dict[str, Any]]:
    response = requests.get(
        "https://rest.uniprot.org/uniprotkb/search",
        params={
            "query": query,
            "format": "json",
            "fields": "accession,gene_primary,gene_synonym,reviewed,fragment,protein_name",
            "sort": "annotation_score desc",
            "size": 25,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("results", [])


def _names(entry: dict[str, Any]) -> list[str]:
    """All protein names of an entry: recommended, alternative and submitted, full and short."""
    description = entry.get("proteinDescription", {})
    name_groups = [description.get("recommendedName", {})]
    name_groups += description.get("alternativeNames", [])
    name_groups += description.get("submissionNames", [])

    names = []
    for group in name_groups:
        if "fullName" in group:
            names.append(group["fullName"]["value"])
        names += [short["value"] for short in group.get("shortNames", [])]
    return names


def _gene_match(entry: dict[str, Any], symbol: str) -> str | None:
    """'gene' if a primary gene name equals the symbol, 'synonym' if a gene synonym does, otherwise None."""
    genes = entry.get("genes", [])
    if any(gene.get("geneName", {}).get("value", "").lower() == symbol.lower() for gene in genes):
        return "gene"
    if any(syn["value"].lower() == symbol.lower() for gene in genes for syn in gene.get("synonyms", [])):
        return "synonym"
    return None


def _name_match(entry: dict[str, Any], symbol: str) -> str | None:
    """'protein_name' if a protein name equals the symbol, otherwise None."""
    return "protein_name" if symbol.lower() in (name.lower() for name in _names(entry)) else None


def _summarize(entry: dict[str, Any]) -> dict[str, Any]:
    genes = entry.get("genes", [])
    names = _names(entry)
    return {
        "accession": entry["primaryAccession"],
        "gene": genes[0].get("geneName", {}).get("value") if genes else None,
        "protein_name": names[0] if names else None,
        "reviewed": "Swiss-Prot" in entry.get("entryType", ""),
    }


def _pick(matches: list[tuple[dict[str, Any], str]], symbol: str) -> dict[str, Any]:
    """Choose among (entry, match_type) pairs that share one review status."""

    # Primary gene before synonym, complete before fragment; the sort is stable, so UniProt's annotation score
    # order decides the rest.
    def rank(match: tuple[dict[str, Any], str]) -> tuple[bool, bool]:
        entry, match_type = match
        return match_type != "gene", "Fragment" in entry.get("proteinDescription", {}).get("flag", "")

    matches = sorted(matches, key=rank)
    best, match_type = matches[0]
    result = {**_summarize(best), "match_type": match_type}

    if result["reviewed"]:
        # Equally good reviewed entries are distinct proteins (e.g. CDKN2A encodes p16 and ARF): don't guess.
        tied = [entry for entry, match in matches if match == match_type]
        if len(tied) > 1:
            return {
                "error": f"Ambiguous: {len(tied)} reviewed UniProt entries match '{symbol}'. Choose a candidate.",
                "candidates": [_summarize(entry) for entry in tied],
            }
    elif len(matches) > 1:
        result["candidates"] = [_summarize(entry) for entry, _ in matches[1:5]]
    return result


@core_mcp.tool()
def get_uniprot_id_by_protein_symbol(
    protein_symbol: Annotated[
        str,
        Field(description="Gene symbol (e.g., 'TP53', 'SYNPO'), gene synonym, or exact protein name (e.g., 'Podocin')"),
    ],
    species: Annotated[
        str,
        Field(description="Organism taxonomy ID (e.g., '9606' for human)"),
    ] = "9606",
) -> dict:
    """Retrieve the UniProt accession for a gene symbol and species. Prefers reviewed (Swiss-Prot) entries.

    Returns:
        dict: accession, gene, protein_name, reviewed, match_type ('gene', 'synonym' or 'protein_name') and other candidates, or error message (with candidates if ambiguous or only partially matching).
    """
    symbol = protein_symbol.replace('"', "").replace("\\", "").strip()
    if not symbol:
        return {"error": "protein_symbol must not be empty."}
    organism = f"organism_id:{str(species).strip()}"
    partial_matches: list[dict[str, Any]] = []

    try:
        # Gene symbols first, protein names as a last resort; reviewed entries before unreviewed ones. Both searches
        # also return partial matches (e.g. "albumin" finds the gene "serum albumin"), so check for an exact match.
        for field, match in [("gene_exact", _gene_match), ("protein_name", _name_match)]:
            for reviewed in ["true", "false"]:
                entries = _search(f'{field}:"{symbol}" AND {organism} AND reviewed:{reviewed}')
                matches = [(entry, match(entry, symbol)) for entry in entries]
                matches = [(entry, match_type) for entry, match_type in matches if match_type]
                if matches:
                    return _pick(matches, symbol)
                if field == "protein_name" and not partial_matches:
                    partial_matches = entries
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to query UniProt: {e!s}"}

    if partial_matches:
        # Offer the partial protein name matches, but don't pick one: the first hit is often the wrong protein (#5)
        return {
            "error": f"No exact match for '{symbol}' in organism {species}. Partial protein name matches are listed.",
            "candidates": [_summarize(entry) for entry in partial_matches[:5]],
        }
    return {"error": f"No UniProt entry found for '{symbol}' in organism {species}."}
