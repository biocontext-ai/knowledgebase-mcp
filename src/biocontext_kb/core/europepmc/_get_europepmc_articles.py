from typing import Annotated, Optional
from urllib.parse import quote

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_europepmc_articles(
    query: Annotated[Optional[str], Field(description="Search query string, not specific to any field")] = None,
    title: Annotated[Optional[str], Field(description="Search term for article titles")] = None,
    abstract: Annotated[Optional[str], Field(description="Search term for article abstracts")] = None,
    author: Annotated[Optional[str], Field(description="Author name (e.g., 'kuehl,malte')")] = None,
    search_type: Annotated[str, Field(description="Search type: 'and' or 'or'")] = "or",
    sort_by: Annotated[
        Optional[str],
        Field(description="Sort by: 'recent' for most recent, 'cited' for most cited or None for no specific sorting"),
    ] = None,
    page_size: Annotated[int, Field(description="Number of results to return", ge=1, le=1000)] = 25,
) -> dict:
    """Query the Europe PMC database for scientific articles.

    Use 'recent' sort for current research queries and 'cited' sort for comprehensive career overviews
    or well-established topics (e.g., "what has author X published on in their career").

    Provide at least one of the following search parameters:
    - query: General search query string
    - title: Search term for article titles
    - abstract: Search term for article abstracts.
    - author: Author name (e.g., "last_name,first_name"). Should not contain spaces.
    These will be combined with the specified search type ("and" or "or").
    For a broad search, prefer the "query" parameter and "or" search type.
    Only use the "and" search type if you want to ensure all terms must match.

    Args:
        query (str, optional): General search query string.
        title (str, optional): Search term for article titles.
        abstract (str, optional): Search term for article abstracts.
        author (str, optional): Author name (e.g., "last_name,first_name"). Should not contain spaces.
        search_type (str): Search type - "and" or "or" (default: "or").
        sort_by (str): Sort by - "recent" for most recent, "cited" for most cited or None for no specific sorting (default: None).
        page_size (int): Number of results to return (default: 25, max: 1000).

    Returns:
        dict: Article search results or error message
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
