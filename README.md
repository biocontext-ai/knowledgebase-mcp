# BioContextAI - Knowledgebase MCP

[![BioContextAI - Registry](https://img.shields.io/badge/Registry-package?style=flat&label=BioContextAI&labelColor=%23fff&color=%233555a1&link=https%3A%2F%2Fbiocontext.ai%2Fregistry)](https://biocontext.ai/registry)
[![Version](https://img.shields.io/pypi/v/biocontext_kb)](https://pypi.org/project/biocontext_kb/)
[![License](https://img.shields.io/pypi/l/biocontext_kb)](https://github.com/biocontext-ai/knowledgebase-mcp)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![GitHub CI](https://github.com/biocontext-ai/knowledgebase-mcp/actions/workflows/ci.yaml/badge.svg)](https://github.com/biocontext-ai/knowledgebase-mcp/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/github/biocontext-ai/knowledgebase-mcp/graph/badge.svg?token=YX4KpHQtsR)](https://codecov.io/github/biocontext-ai/knowledgebase-mcp)

A Model Context Protocol (MCP) server for biomedical research that provides a standardized connection layer between artificial intelligence systems and biomedical resources. Documentation and usage guides are available at: https://biocontext.ai

## Overview

**BioContextAI Knowledgebase MCP** is an MCP server implementation for common biomedical resources, enabling agentic large language models (LLMs) to retrieve verified information and perform domain-specific tasks. Unlike previous approaches that required custom integration for each resource, BioContextAI KB MCP provides a unified access layer through the Model Context Protocol that enables interoperability between AI systems and domain-specific data sources.

The Knowledgebase MCP is available both as:

- An open-source software package for local hosting (see [Self-hosting](#self-hosting))
- A remote server for setup-free integration at https://mcp.biocontext.ai/mcp/ (subject to fair use)

> [!WARNING]
> If possible, we encourage you to run BioContextAI Knowledgebase MCP locally to avoid rate limits and ensure the service's availability for applications that rely on remote hosting.

The Knowledgebase MCP is part of the wider [BioContextAI project](https://biocontext.ai). The **BioContextAI Registry** catalogues community servers that expose biomedical databases and analysis tools, providing the community with a resource for tool discovery and distribution. The registry index can be found at: https://biocontext.ai/registry.

## Citation

If our work is useful to your research, please cite it as below.

> TBA.

## Implemented Tools

BioContextAI Knowledgebase MCP exposes a number of external biomedical APIs. You can think of BioContextAI as a browser for your LLM that allows it to find relevant information across these knowledge bases. Please make sure to adhere to the usage limits (e.g., rate limits) of the respective services when using BioContextAI Knowledgebase MCP.
If you use data from these services in your research, please make sure to cite both BioContextAI as well as the respective data source/tool.

> [!WARNING]
> The data accessed through these APIs is not covered by the BioContextAI Knowledgebase MCP license. You are responsible for ensuring that your use of the data aligns with permitted practices.

### Tools

- [Antibody Registry](https://antibodyregistry.org) - Gene id conversion
- [bioRxiv/medRxiv](https://biorxiv.org/) - Recent preprint search and metadata access
- [Ensembl](https://www.ensembl.org/info/data/rest.html) - Gene id conversion
- [EuropePMC](https://europepmc.org/) - Literature search and full-text access
- [Google Scholar](https://scholar.google.com/) - Academic publication and author search (only available for local use due to rate limiting)
- [InterPro](https://www.ebi.ac.uk/interpro/) - Protein families, domains, and functional sites classification
- [KEGG](https://www.kegg.jp/) - Pathways, gene and drug-drug interaction database (only available for local use due to licensing restrictions)
- [OpenTargets](https://platform.opentargets.org/api) - Target-disease associations
- [PanglaoDB](https://panglaodb.se/) - Single-cell RNA-sequencing cell type markers
- [PRIDE](https://www.ebi.ac.uk/pride/archive/) - Proteomics data repository for mass spectrometry data
- [Protein Atlas](https://www.proteinatlas.org/) - Protein expression data
- [Reactome](https://reactome.org/) - Pathways database
- [STRING](https://string-db.org/) - Protein-protein interaction networks
- [AlphaFold DB](https://alphafold.ebi.ac.uk/) - Tertiary protein structure predictions

## License overview

The above data is provided without warranty and may be inaccurate or out-of-date. Please verify your use case is allowed.

### OpenAPI MCP servers

`FastMCP` allows for easy conversion of REST endpoints following the OpenAPI specification into MCP servers. We have added code to automatically create such servers based on schemas provided through a configuration file, so that users deploying their own version of BioContextAI can easily extend the list of available tools. The configuration file is located at `src/biocontext_kb/openapi/config.yaml`. By default, no OpenAPI servers are included, but you can edit the configuration file to add services.

## Self-hosting

Clone the latest version of this repository:

```bash
git clone https://github.com/biocontext-ai/core-mcp-server.git
cd core-mcp-server
```

Then run one of the following:

1. Docker setup (gunicorn with multiple uvicorn workers):

```bash
# Build the docker container
docker build -t biocontext_kb:latest .
docker run -p 127.0.0.1:8000:8000 biocontext_kb:latest
```

This exposes your MCP server at: http://127.0.0.1:8000/mcp/

> [!WARNING]
> For public deployments, you should disabled unnecessary ports and access your MCP server through a reverse proxy, e.g., Nginx or Caddy. You may also want to configure the running user and the directory to have limited rights, use Docker or podman in a rootless setup and take additional security measures like DDOS protection with Cloudflare or fail2ban.

2. Local setup with `uv`, with streamable HTTP and uvicorn:

```bash
uv build
export MCP_ENVIRONMENT=PRODUCTION
export PORT=8000
biocontext_kb
```

3. Locall setup with `uv`, with stdio transport:

```bash
uv build
export MCP_ENVIRONMENT=DEVELOPMENT
biocontext_kb
```

4. Locall setup with Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "biocontext_kb": {
      "command": "uvx",
      "args": [
        "biocontext_kb@latest"
      ],
      "env": {
        "UV_PYTHON": "3.12"
      }
    }
  }
}
```

**Don't forget to restart Claude to apply the changes.**

5. Locally, with your coding agents in VS Code (`.vscode/mcp.json`) or Cursor (`.cursor/mcp.json`) or WindSurf (`.codeium/windsurf/mcp_config.json`):

```jsonc
{
  // VS Code: "servers"
  "mcpServers": {
    "biocontext_kb": {
      // if it doesn't work, replace with the `which uvx` path (installation via Homebrew recommended on macOS)
      "command": "uvx",
      "args": [
        "biocontext_kb@latest"
      ],
    }
  }
}
```

When using Windows and WSL2 the above config needs to be adapted as follows:

```jsonc
{
  // VS Code: "servers"
  "mcpServers": {
    "biocontext_kb": {
      "command": "wsl",
      "args": [
        "~/.local/bin/uvx", // set to the path to your `uvx`
        "biocontext_kb"
      ]
    }
  }
}
```

6. Locally, with your own MCP clients:

- Follow the `PydanticAI` [setup guide](https://ai.pydantic.dev/mcp/client/)
- Follow the `FastMCP` [setup guide](https://gofastmcp.com/getting-started/welcome)
- Follow the `mcp-use` [setup guide](https://github.com/mcp-use/mcp-use)

## Resources

- Project documentation: https://biocontext.ai
- API documentationt: https://docs.kb.biocontext.ai/
- BioContextAI Registry: https://github.com/biocontext-ai/registry
- Chat Interface: https://biocontext.ai/chat

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

> [!WARNING]
> The Apache 2.0 License only applies to the code provided in this repository. For usage limitations and licenses of the individually integrated APIs, users should directly refer to the respective API providers. We provide an overview below.

### Data Sources and Licensing

| Data Source                        | License                         | URL                                                              | Notes                                                               |
| ---------------------------------- | ------------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| AlphaFold (EMBL-EBI)               | CC BY 4.0                       | https://alphafold.ebi.ac.uk/                                     |                                                                     |
| Antibody Registry (RRIDs)          | CC0 (metadata: CC-NC)           | https://www.antibodyregistry.org/faq                             | Commercial reuse restrictions on some metadata                      |
| bioRxiv/medRxiv                    | CC BY 4.0                       | https://www.biorxiv.org/about/FAQ                                | Preprint content licenses vary                                      |
| ClinicalTrials.gov API             | Terms of Service                | https://clinicaltrials.gov/about-site/terms-conditions           | Attribution required                                                |
| Ensembl                            | No restrictions\*               | https://www.ensembl.org/info/about/legal/disclaimer.html         | \*Some third-party data may have restrictions                       |
| EuropePMC                          | Various/Copyright protected     | https://europepmc.org/Copyright                                  | Individual article licenses vary                                    |
| Google Scholar                     | Terms of Service                | https://scholar.google.com/intl/en/scholar/terms.html            | Rate limiting; use responsibly                                      |
| Grants.gov API                     | Terms of Service                | https://www.grants.gov/api/terms-conditions                      | Attribution required                                                |
| Human Protein Atlas                | CC BY-SA 4.0                    | https://www.proteinatlas.org/about/licence                       |                                                                     |
| InterPro                           | CC0 1.0 Universal               | https://www.ebi.ac.uk/interpro/                                  | Includes InterPro, Pfam, PRINTS, and SFLD data                      |
| KEGG                               | Proprietary (Free academic use) | https://www.kegg.jp/kegg/legal.html                              | Commercial services/remote hosting not permitted                    |
| Ontology Lookup Service (EMBL-EBI) | Generally CC0/CC BY             | https://www.ebi.ac.uk/licencing/                                 | Refer to EMBL-EBI general licensing                                 |
| Open Targets                       | CC0 1.0                         | https://platform-docs.opentargets.org/licence                    |                                                                     |
| OpenFDA                            | CC0 1.0 Universal\*             | https://open.fda.gov/license/                                    | \*Some data may have restrictions                                   |
| PanglaoDB                          | Public data                     | https://panglaodb.se/about.html                                  | All data are public                                                 |
| PRIDE                              | CC0/CC BY 4.0\*                 | https://www.ebi.ac.uk/pride/markdownpage/license                 | \*CC0 for datasets from June 2018+, CC BY 4.0 for derived resources |
| Reactome                           | CC0                             | https://reactome.org/license                                     |                                                                     |
| STRING                             | CC BY 4.0                       | https://string-db.org/cgi/access?footer_active_subpage=licensing |                                                                     |
| UniProt                            | CC BY 4.0                       | https://www.uniprot.org/help/license                             |                                                                     |

### Disclaimer

**Users are solely responsible for ensuring compliance with all applicable license terms and conditions when accessing data through this MCP server.** The licenses and terms listed above are subject to change, and additional citation requirements may apply for specific datasets or publications. Before using any data for commercial purposes, redistribution, or publication, please review the current license terms directly from each data source. Some data sources may have additional restrictions not fully captured in this summary.

For KEGG data specifically, please note that while academic use is permitted, providing commercial services or remote hosting using KEGG data is not allowed under their proprietary license terms.
