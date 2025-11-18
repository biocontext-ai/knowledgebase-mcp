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
        Field(description="Search query (e.g., 'machine learning' or 'author:\"John Smith\" deep learning')"),
    ],
    max_results: Annotated[int, Field(description="Maximum number of publications to return (1-50)", ge=1, le=50)] = 10,
    use_proxy: Annotated[bool, Field(description="Use free proxies to avoid rate limiting")] = True,
) -> Dict[str, Any]:
    """Search Google Scholar for publications with support for author search using 'author:"Name"' syntax. WARNING: Use responsibly, may block excessive queries.

    Returns:
        dict: Publications list with title, authors, venue, year, citations, abstract, bib entry or error message.
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
