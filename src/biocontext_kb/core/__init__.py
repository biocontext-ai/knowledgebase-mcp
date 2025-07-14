import os

from ._server import core_mcp
from .alphafold import *
from .antibodyregistry import *
from .biorxiv import *
from .clinicaltrials import *
from .ensembl import *
from .europepmc import *
from .grants._search_grants_gov import *
from .interpro import *
from .ols import *
from .openfda import *
from .opentargets import *
from .panglaodb import *
from .pride import *
from .proteinatlas import *
from .reactome import *
from .stringdb import *
from .uniprot import *

# KEGG cannot freely be included in provided services, even for academic use, due to licensing restrictions.
if os.getenv("MCP_ENVIRONMENT") != "PRODUCTION" or os.getenv("MCP_INCLUDE_KEGG", "false").lower() == "true":
    from .kegg import *

# Google Scholar is rate-limited and not suitable for production use, but can be used locally for testing.
if os.getenv("MCP_ENVIRONMENT") != "PRODUCTION" or os.getenv("MCP_INCLUDE_SCHOLARLY", "false").lower() == "true":
    from .scholarly import *

__all__ = [
    "core_mcp",
]
