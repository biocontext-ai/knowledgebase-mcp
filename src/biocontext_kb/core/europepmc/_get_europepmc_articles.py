from typing import Annotated, Optional
from urllib.parse import quote

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_europepmc_articles(
    query: Annotated[Optional[str], Field(description="General search query")] = None,
    title: Annotated[Optional[str], Field(description="Search in article titles")] = None,
    abstract: Annotated[Optional[str], Field(description="Search in abstracts")] = None,
    author: Annotated[Optional[str], Field(description="Author name (e.g., 'lastname,firstname')")] = None,
    search_type: Annotated[str, Field(description="'and' or 'or' (default: 'or')")] = "or",
    sort_by: Annotated[
        Optional[str],
        Field(description="'recent' or 'cited' (default: none)"),
    ] = None,
    page_size: Annotated[int, Field(description="Results per page (1-1000)", ge=1, le=1000)] = 25,
) -> dict:
    """Search Europe PMC articles by query, title, abstract, or author. Combine search terms with 'and'/'or' logic.

    Returns:
        dict: Search results with resultList containing articles (title, authors, abstract, journal, PMC/DOI IDs) or error message.
    """
    # Ensure at least one search parameter was provided
    if not any([query, title, abstract, author]):
        return {"error": "At least one of query, title, abstract, or author must be provided"}

    # Build query components
    query_parts = []

    if query:
        query_parts.append(query)

    if title:
        query_parts.append(f"title:{title}")

    if abstract:
        query_parts.append(f"abstract:{abstract}")

    if author:
        query_parts.append(f"auth:{author}")

    # Join query parts based on search type
    query = " AND ".join(query_parts) if search_type.lower() == "and" else " OR ".join(query_parts)

    # If multiple parts and not explicitly AND, wrap in parentheses for OR
    if len(query_parts) > 1 and search_type.lower() == "or":
        query = f"({query})"

    # Add sort parameter
    if sort_by is not None:
        if sort_by.lower() == "cited":
            query += " sort_cited:y"
        else:  # default to recent
            query += " sort_date:y"

    # URL encode the query
    encoded_query = quote(query)

    url = f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?query={encoded_query}&format=json&resultType=core&pageSize={page_size}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch Europe PMC articles: {e!s}"}
