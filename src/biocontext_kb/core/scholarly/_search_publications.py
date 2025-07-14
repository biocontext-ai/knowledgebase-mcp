import logging
from typing import Annotated, Any, Dict

from pydantic import Field
from scholarly import ProxyGenerator, scholarly

from biocontext_kb.core._server import core_mcp

logger = logging.getLogger(__name__)


@core_mcp.tool()
def search_google_scholar_publications(
    query: Annotated[
        str,
        Field(
            description="Search query for publications (e.g., 'machine learning' or 'author:\"John Smith\" deep learning')"
        ),
    ],
    max_results: Annotated[int, Field(description="Maximum number of publications to return", ge=1, le=50)] = 10,
    use_proxy: Annotated[bool, Field(description="Whether to use free proxies to avoid rate limiting")] = True,
) -> Dict[str, Any]:
    """Search for publications on Google Scholar.

    Supports advanced search operators including author search using 'author:"Name"' syntax.

    Examples:
    - 'machine learning' - General topic search
    - 'author:"John Smith"' - Publications by specific author
    - 'author:"John Smith" neural networks' - Author's work on specific topic

    WARNING: Google Scholar may block requests and IP addresses for excessive queries.
    Publication searches are particularly prone to triggering anti-bot measures.
    This tool automatically uses free proxies to mitigate blocking, but use responsibly.

    For academic research, consider using alternative databases like PubMed/EuropePMC
    when possible to reduce load on Google Scholar.

    Args:
        query (str): Search query for publications. Use 'author:"Name"' to search by author.
        max_results (int): Maximum number of publications to return (default: 10, max: 50).
        use_proxy (bool): Whether to use free proxies to avoid rate limiting (default: True).

    Returns:
        dict: Publication search results or error message
    """
    try:
        # Set up proxy if requested
        if use_proxy:
            try:
                pg = ProxyGenerator()
                pg.FreeProxies()
                scholarly.use_proxy(pg)
                logger.info("Proxy configured for Google Scholar requests")
            except Exception as e:
                logger.warning(f"Failed to set up proxy: {e}")
                # Continue without proxy

        # Search for publications
        search_query = scholarly.search_pubs(query)

        publications = []

        for count, pub in enumerate(search_query):
            if count >= max_results:
                break

            # Extract publication information
            bib = pub.get("bib", {})
            pub_info = {
                "title": bib.get("title", ""),
                "author": bib.get("author", ""),
                "venue": bib.get("venue", ""),
                "pub_year": bib.get("pub_year", ""),
                "abstract": bib.get("abstract", ""),
                "pub_url": bib.get("pub_url", ""),
                "eprint_url": pub.get("eprint_url", ""),
                "num_citations": pub.get("num_citations", 0),
                "citedby_url": pub.get("citedby_url", ""),
                "url_scholarbib": pub.get("url_scholarbib", ""),
            }

            publications.append(pub_info)

        return {"query": query, "total_found": len(publications), "publications": publications}

    except Exception as e:
        logger.error(f"Error searching Google Scholar publications: {e}")
        return {
            "error": f"Failed to search Google Scholar publications: {e!s}",
            "note": "Google Scholar may be blocking requests. Publication searches are particularly risky. Try again later or use alternative databases like PubMed/EuropePMC.",
        }
