.. _index:


==========
BioContextAI Knowledgebase MCP
==========

Overview
--------

BioContextAI Knowledgebase MCP implements MCP servers for common biomedical resources, enabling agentic large language models (LLMs) to retrieve verified information and perform domain-specific tasks. Unlike previous approaches requiring custom integration for each resource, BioContextAI provides a unified access layer through the Model Context Protocol that enables interoperability between AI systems and domain-specific data sources.

BioContextAI is available both as:

- An open-source software package for local hosting (see :ref:`Self-hosting <selfhosting>`)
- A remote server for setup-free integration at https://mcp.biocontext.ai/mcp/ (subject to fair use)

The **BioContextAI Registry** catalogues community servers that expose biomedical databases and analysis tools, providing the community with a resource for tool discovery and distribution. The registry index can be found at: https://biocontext.ai/registry.

Documentation
----------------

Detailled documentation about the BioContextAI Knowledgebase MCP and the overall BioContextAI project can be found at https://biocontext.ai/docs.

This documentation is auto-generated from the source code and provides the API documentation. For other documentation, please refer to the main BioContextAI documentation at https://biocontext.ai/docs.

.. toctree::
    :caption: Start
    :maxdepth: 4
    :glob:

    install
    client_example

.. toctree::
    :caption: API Documentation
    :maxdepth: 4
    :glob:

    autoapi/biocontext_kb/index
