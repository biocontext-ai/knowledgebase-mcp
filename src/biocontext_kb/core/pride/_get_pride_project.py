from typing import Annotated

import requests
from pydantic import Field

from biocontext_kb.core._server import core_mcp


@core_mcp.tool()
def get_pride_project(
    project_accession: Annotated[
        str,
        Field(description="The PRIDE project accession (e.g., 'PRD000001')"),
    ],
    include_files: Annotated[
        bool,
        Field(description="Whether to include file information for the project"),
    ] = False,
    include_similar_projects: Annotated[
        bool,
        Field(description="Whether to include similar projects based on metadata"),
    ] = False,
) -> dict:
    """Get detailed information about a specific PRIDE project.

    PRIDE (PRoteomics IDEntifications) is a public repository for mass spectrometry
    proteomics data. This function retrieves comprehensive information about a
    specific project including metadata, experimental details, and optionally
    associated files and similar projects.

    Args:
        project_accession (str): The PRIDE project accession (e.g., "PRD000001").
        include_files (bool, optional): Whether to include file information. Defaults to False.
        include_similar_projects (bool, optional): Whether to include similar projects. Defaults to False.

    Returns:
        dict: Project information including metadata, experimental details, and optional file/similar project data
    """
    base_url = "https://www.ebi.ac.uk/pride/ws/archive/v3"

    try:
        # Get basic project information
        project_url = f"{base_url}/projects/{project_accession}"
        response = requests.get(project_url)
        response.raise_for_status()

        project_data = response.json()

        if not project_data:
            return {"error": f"No data found for PRIDE project {project_accession}"}

        result = project_data

        # Optionally include file information
        if include_files:
            try:
                files_url = f"{base_url}/projects/{project_accession}/files"
                files_response = requests.get(files_url, params={"pageSize": 20})
                if files_response.status_code == 200:
                    files_data = files_response.json()
                    result["files"] = files_data[:20]  # Limit to first 20 files

                    # Get file count
                    count_url = f"{base_url}/projects/{project_accession}/files/count"
                    count_response = requests.get(count_url)
                    if count_response.status_code == 200:
                        result["total_files"] = count_response.json()

            except Exception:
                result["files"] = {"error": "Could not fetch file information"}

        # Optionally include similar projects
        if include_similar_projects:
            try:
                similar_url = f"{base_url}/projects/{project_accession}/similarProjects"
                similar_response = requests.get(similar_url, params={"pageSize": 10})
                if similar_response.status_code == 200:
                    similar_data = similar_response.json()
                    result["similar_projects"] = similar_data[:10]  # Limit to first 10
            except Exception:
                result["similar_projects"] = {"error": "Could not fetch similar projects"}

        return result

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"PRIDE project {project_accession} not found"}
        return {"error": f"HTTP error: {e}"}
    except Exception as e:
        return {"error": f"Exception occurred: {e!s}"}
