import logging
from datetime import datetime, timedelta
from typing import Annotated, Any, Dict, Optional

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp

logger = logging.getLogger(__name__)


@core_mcp.tool()
def get_recent_biorxiv_preprints(
    server: Annotated[str, Field(description="Server to search: 'biorxiv' or 'medrxiv'")] = "biorxiv",
    start_date: Annotated[Optional[str], Field(description="Start date in YYYY-MM-DD format")] = None,
    end_date: Annotated[Optional[str], Field(description="End date in YYYY-MM-DD format")] = None,
    days: Annotated[
        Optional[int], Field(description="Number of recent days to search (alternative to date range)", ge=1, le=365)
    ] = None,
    recent_count: Annotated[
        Optional[int], Field(description="Number of most recent preprints (alternative to date range)", ge=1, le=1000)
    ] = None,
    category: Annotated[
        Optional[str], Field(description="Subject category filter (e.g., 'cell biology', 'neuroscience')")
    ] = None,
    cursor: Annotated[int, Field(description="Starting position for pagination", ge=0)] = 0,
    max_results: Annotated[int, Field(description="Maximum number of results to return", ge=1, le=500)] = 100,
) -> Dict[str, Any]:
    """Get recent preprints from bioRxiv or medRxiv.

    This tool searches the bioRxiv and medRxiv preprint servers for research papers.
    You can search by date range, recent posts, or most recent papers.
    Results are paginated with up to 100 papers per API call.

    Args:
        server (str): Server to search - 'biorxiv' or 'medrxiv' (default: 'biorxiv').
        start_date (str, optional): Start date in YYYY-MM-DD format.
        end_date (str, optional): End date in YYYY-MM-DD format.
        days (int, optional): Number of recent days to search (1-365).
        recent_count (int, optional): Number of most recent preprints (1-1000).
        category (str, optional): Subject category filter (e.g., 'cell biology', 'neuroscience').
        cursor (int): Starting position for pagination (default: 0).
        max_results (int): Maximum number of results to return (default: 100, max: 500).

    Returns:
        dict: Preprint search results or error message
    """
    # Validate server
    if server.lower() not in ["biorxiv", "medrxiv"]:
        return {"error": "Server must be 'biorxiv' or 'medrxiv'"}

    server = server.lower()

    # Validate input parameters - only one search method should be specified
    search_methods = [start_date and end_date, days, recent_count]
    if sum(bool(method) for method in search_methods) != 1:
        return {"error": "Specify exactly one of: date range (start_date + end_date), days, or recent_count"}

    try:
        # Build the interval parameter
        interval = ""
        if start_date and end_date:
            # Validate date format
            try:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return {"error": "Dates must be in YYYY-MM-DD format"}

            # Validate date range (start should be before or equal to end)
            if start_date_obj > end_date_obj:
                return {"error": "Start date must be before or equal to end date"}

            interval = f"{start_date}/{end_date}"
        elif days:
            # Convert days to actual date range
            end_date_obj = datetime.now()
            start_date_obj = end_date_obj - timedelta(days=days)
            start_date_str = start_date_obj.strftime("%Y-%m-%d")
            end_date_str = end_date_obj.strftime("%Y-%m-%d")
            interval = f"{start_date_str}/{end_date_str}"
        elif recent_count:
            interval = str(recent_count)

        # Build URL
        base_url = f"https://api.biorxiv.org/details/{server}/{interval}/{cursor}/json"

        # Add category filter if specified
        params = {}
        if category and ((start_date and end_date) or days):  # Category works with date ranges
            params["category"] = category.replace(" ", "_")

        # Make request
        response = requests.get(base_url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        # Extract and limit results
        collection = data.get("collection", [])
        limited_results = collection[:max_results]

        # Clean up the results for better LLM consumption
        processed_results = []
        for paper in limited_results:
            processed_paper = {
                "doi": paper.get("doi", ""),
                "title": paper.get("title", ""),
                "authors": paper.get("authors", ""),
                "corresponding_author": paper.get("author_corresponding", ""),
                "corresponding_institution": paper.get("author_corresponding_institution", ""),
                "date": paper.get("date", ""),
                "version": paper.get("version", ""),
                "type": paper.get("type", ""),
                "license": paper.get("license", ""),
                "category": paper.get("category", ""),
                "abstract": paper.get("abstract", ""),
                "published": paper.get("published", ""),
                "server": paper.get("server", server),
            }
            processed_results.append(processed_paper)

        # Get pagination info from messages
        messages = data.get("messages", [])
        pagination_info = {}
        for message in messages:
            if "cursor" in message.get("text", "").lower():
                pagination_info["cursor_info"] = message.get("text", "")
            if "count" in message.get("text", "").lower():
                pagination_info["count_info"] = message.get("text", "")

        return {
            "server": server,
            "search_params": {
                "interval": interval,
                "category": category,
                "cursor": cursor,
                "original_days": days if days else None,
            },
            "total_returned": len(processed_results),
            "papers": processed_results,
            "pagination": pagination_info,
            "messages": messages,
        }

    except requests.exceptions.RequestException as e:
        logger.error(f"Error searching {server}: {e}")
        return {"error": f"Failed to search {server}: {e!s}"}
    except Exception as e:
        logger.error(f"Unexpected error searching {server}: {e}")
        return {"error": f"Unexpected error: {e!s}"}
