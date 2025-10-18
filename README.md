# BioContextAI - Knowledgebase MCP

[![BioContextAI - Registry](https://img.shields.io/badge/Registry-package?style=flat&label=BioContextAI&labelColor=%23fff&color=%233555a1&link=https%3A%2F%2Fbiocontext.ai%2Fregistry)](https://biocontext.ai/registry/biocontext-ai/knowledgebase-mcp)
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

- An open-source software package for local hosting (see [Installation](#installation)) - **Choose this option for Claude Desktop, IDEs or your own agentic systems**
- A remote server for setup-free integration at https://mcp.biocontext.ai/mcp/ (for testing purposes only, subject to fair use)

> [!WARNING]
> If possible, we encourage you to run BioContextAI Knowledgebase MCP locally to avoid rate limits and ensure the service's availability for applications that rely on remote hosting.

The Knowledgebase MCP is part of the wider [BioContextAI project](https://biocontext.ai). The **BioContextAI Registry** catalogues community servers that expose biomedical databases and analysis tools, providing the community with a resource for tool discovery and distribution. The registry index can be found at: https://biocontext.ai/registry.

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

### OpenAPI MCP Servers

`FastMCP` allows for easy conversion of REST endpoints following the OpenAPI specification into MCP servers. We have added code to automatically create such servers based on schemas provided through a configuration file, so that users deploying their own version of BioContextAI can easily extend the list of available tools. The configuration file is located at `src/biocontext_kb/openapi/config.yaml`. By default, no OpenAPI servers are included, but you can edit the configuration file to add services.

## Installation

1. **Local setup with Claude Desktop**:

Edit your `claude_desktop_config.json` file. To find it, click on your name and then “Settings”. Next, click on “Developer” to see “Local MCP servers” and then click on “Edit Config”.

```jsonc
{
  "mcpServers": {
    "biocontext_kb": {
      "command": "uvx", // On Mac, use "brew install uv"
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

> [!WARNING]
> Don't forget to restart Claude to apply the changes.

2. **Local setup with `uv`**

Run the server with streamable HTTP and uvicorn:

```bash
export MCP_ENVIRONMENT=PRODUCTION && export PORT=8000 && uvx biocontext_kb
```

Run the server with stdio transport:

```bash
export MCP_ENVIRONMENT=DEVELOPMENT && uvx biocontext_kb
```

3. **Local setup with IDEs**

Change the configuration file of your coding agents, e.g., VS Code (`.vscode/mcp.json`), Cursor (`.cursor/mcp.json`), or WindSurf (`.codeium/windsurf/mcp_config.json`):

```jsonc
{
  // VS Code: Use "servers" instead of "mcpServers"
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

4. **Docker**

Clone the latest version of this repository:

```bash
git clone https://github.com/biocontext-ai/knowlegebase-mcp.git
cd knowlegebase-mcp
```

Then build the container, running gunicorn with multiple uvicorn workers:

```bash
# Build the docker container
docker build -t biocontext_kb:latest .
docker run -p 127.0.0.1:8000:8000 biocontext_kb:latest
```

This exposes your MCP server at: http://127.0.0.1:8000/mcp/

> [!WARNING]
> For public deployments, you should disable unnecessary ports and access your MCP server through a reverse proxy, e.g., Nginx or Caddy. You may also want to configure the running user and the directory to have limited rights, use Docker or podman in a rootless setup and take additional security measures like DDOS protection with Cloudflare or fail2ban.

### MCP Clients

To develop your own agentic systems that make use of the MCP server, you may want to consider some of the following options:

- [PydanticAI](https://ai.pydantic.dev/mcp/client/)
- [FastMCP](https://gofastmcp.com/getting-started/welcome)
- [Langchain MCP adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [mcp-use](https://github.com/mcp-use/mcp-use)

## Preprint & Documentation

You can find our preprint here: [https://www.biorxiv.org/content/10.1101/2025.07.21.665729v1.full.pdf](https://www.biorxiv.org/content/10.1101/2025.07.21.665729v1.full.pdf).

If our work is useful to your research, please cite it as below.

```bibtex
@misc{kuehlCommunitybasedBiomedicalContext2025,
  title = {Community-Based Biomedical Context to Unlock Agentic Systems},
  author = {Kuehl, Malte and Schaub, Darius P. and Carli, Francesco and Heumos, Lukas and {Fern{\'a}ndez-Zapata}, Camila and Kaiser, Nico and Schaul, Jonathan and Panzer, Ulf and Bonn, Stefan and Lobentanzer, Sebastian and {Saez-Rodriguez}, Julio and Puelles, Victor G.},
  year = {2025},
  month = jul,
  pages = {2025.07.21.665729},
  publisher = {bioRxiv},
  issn = {2692-8205},
  doi = {10.1101/2025.07.21.665729},
  urldate = {2025-07-28},
  abstract = {Large language models (LLMs) face reliability challenges stemming from hallucinations and insufficient access to validated scientific resources. Existing solutions are often fragmented and limited to specific applications, hindering broader adoption and interoperability. Here, we present Biomedical Context for Artificial Intelligence (BioContextAI), an open-source initiative centered on Model Context Protocol (MCP) servers to address these limitations. BioContextAI provides a community-oriented registry for discovering domain-specific MCP servers and a proof-of-concept server implementation that integrates widely-used biomedical knowledgebases. By enabling standardized access to validated scientific knowledge, BioContextAI aims to facilitate the development of composable agentic systems for biomedical research. Together, this work contributes to an emerging ecosystem of community-driven approaches for expanding the capabilities and reliability of biomedical AI systems.},
  archiveprefix = {bioRxiv},
  copyright = {{\copyright} 2025, Posted by Cold Spring Harbor Laboratory. This pre-print is available under a Creative Commons License (Attribution 4.0 International), CC BY 4.0, as described at http://creativecommons.org/licenses/by/4.0/},
}
```

### Further Resources

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
