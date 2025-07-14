"""Google Scholar tools for searching authors and publications.

WARNING: Google Scholar may block requests and IP addresses for excessive queries.
These tools automatically use free proxies to mitigate blocking, but use responsibly.
For academic research, consider using alternative databases like PubMed/EuropePMC
when possible to reduce load on Google Scholar.
"""

from ._search_publications import search_google_scholar_publications

__all__ = [
    "search_google_scholar_publications",
]
