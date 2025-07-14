from enum import Enum
from typing import Annotated, List, Optional, Union

from pydantic import BaseModel, Field, field_validator

from biocontext_kb.core._server import core_mcp
from biocontext_kb.core.kegg._execute_kegg_query import execute_kegg_query


class KeggOperation(str, Enum):
    """KEGG API operations.

    These operations correspond to the different API endpoints in the KEGG REST API.
    For detailed information on each operation, see: https://www.kegg.jp/kegg/rest/keggapi.html
    """

    INFO = "info"  # Display database release information
    LIST = "list"  # Obtain a list of entry identifiers
    FIND = "find"  # Find entries with matching keywords
    GET = "get"  # Retrieve given database entries
    CONV = "conv"  # Convert between KEGG and outside database identifiers
    LINK = "link"  # Find related entries by cross-references
    DDI = "ddi"  # Find adverse drug-drug interactions


class KeggDatabase(str, Enum):
    """Primary KEGG databases.

    These databases contain different types of biological data in the KEGG system.
    Pathway and pathway-related databases: pathway, brite, module, ko
    Genes and genomes: genes, genome (organism-specific databases use KEGG organism codes)
    Chemical compounds: compound, glycan, reaction, rclass, enzyme
    Disease, drugs, and variants: variant, disease, drug, dgroup
    """

    KEGG = "kegg"  # All KEGG databases combined
    PATHWAY = "pathway"  # KEGG pathway maps
    BRITE = "brite"  # BRITE functional hierarchies
    MODULE = "module"  # KEGG modules
    ORTHOLOGY = "ko"  # KEGG orthology
    GENOME = "genome"  # KEGG organisms
    COMPOUND = "compound"  # Chemical compounds
    GLYCAN = "glycan"  # Glycans
    REACTION = "reaction"  # Biochemical reactions
    RCLASS = "rclass"  # Reaction classes
    ENZYME = "enzyme"  # Enzyme nomenclature
    NETWORK = "network"  # Network elements
    VARIANT = "variant"  # Human gene variants
    DISEASE = "disease"  # Human diseases
    DRUG = "drug"  # Drugs
    DGROUP = "dgroup"  # Drug groups
    GENES = "genes"  # Genes in KEGG organisms (composite database)
    LIGAND = "ligand"  # Collection of chemical databases
    ORGANISM = "organism"  # Special case for list operation to get organism codes


class KeggOutsideDb(str, Enum):
    """Outside databases integrated in KEGG.

    These external databases can be used in CONV (conversion) and LINK operations.
    """

    PUBMED = "pubmed"  # PubMed literature database
    NCBI_GENEID = "ncbi-geneid"  # NCBI Gene IDs
    NCBI_PROTEINID = "ncbi-proteinid"  # NCBI Protein IDs
    UNIPROT = "uniprot"  # UniProt protein database
    PUBCHEM = "pubchem"  # PubChem compound database
    CHEBI = "chebi"  # Chemical Entities of Biological Interest
    ATC = "atc"  # Anatomical Therapeutic Chemical Classification System
    JTC = "jtc"  # Japanese therapeutic category
    NDC = "ndc"  # National Drug Code (USA)
    YJ = "yj"  # YJ codes (Japan drug products)
    YK = "yk"  # Part of Korosho code (Japan)


class KeggOption(str, Enum):
    """Options for GET operation.

    These options specify the format or type of data to retrieve for database entries.
    """

    AASEQ = "aaseq"  # Amino acid sequence
    NTSEQ = "ntseq"  # Nucleotide sequence
    MOL = "mol"  # Chemical structure in MOL format
    KCF = "kcf"  # Chemical structure in KCF format
    IMAGE = "image"  # Image file (pathway maps, compound structures)
    CONF = "conf"  # Configuration file (for pathway maps)
    KGML = "kgml"  # KEGG Markup Language file (for pathway maps)
    JSON = "json"  # JSON format (for brite hierarchies)


class KeggFindOption(str, Enum):
    """Options for FIND operation on compounds/drugs.

    These options specify the search criteria for chemical compounds and drugs.
    """

    FORMULA = "formula"  # Search by chemical formula
    EXACT_MASS = "exact_mass"  # Search by exact mass
    MOL_WEIGHT = "mol_weight"  # Search by molecular weight
    NOP = "nop"  # No processing (literal search)


class KeggRdfFormat(str, Enum):
    """RDF output formats for LINK with RDF option.

    These options specify the format of returned RDF data.
    """

    TURTLE = "turtle"  # Turtle RDF format
    N_TRIPLE = "n-triple"  # N-Triples RDF format


class KeggConfig(BaseModel):
    """Configuration for KEGG API queries.

    This model encapsulates the parameters needed to construct a valid KEGG API request.
    The parameters required depend on the operation being performed.
    """

    operation: KeggOperation
    database: Optional[Union[KeggDatabase, KeggOutsideDb, str]] = None
    target_db: Optional[Union[KeggDatabase, KeggOutsideDb, str]] = None
    source_db: Optional[Union[KeggDatabase, KeggOutsideDb, str]] = None
    query: Optional[str] = None
    option: Optional[Union[KeggOption, KeggFindOption, KeggRdfFormat]] = None
    entries: Optional[List[str]] = Field(default_factory=lambda: [])

    @field_validator("database", "target_db", "source_db", mode="before")
    @classmethod
    def validate_db(cls, v):
        """Allow organism codes as database values.

        This validator handles KEGG organism codes (like 'hsa' for human) as valid database values.
        """
        if v is None:
            return v
        # Check if value is in one of the enums
        try:
            return KeggDatabase(v)
        except ValueError:
            try:
                return KeggOutsideDb(v)
            except ValueError:
                # Assume it's an organism code or custom string
                return v

    def build_path(self) -> str:
        """Build the API path based on the configuration.

        This method constructs the URL path for the KEGG API request based on the
        operation and parameters provided.
        """
        path_parts = [self.operation.value.lower()]

        if self.operation == KeggOperation.INFO:
            if self.database:
                path_parts.append(str(self.database.value if isinstance(self.database, Enum) else self.database))

        elif self.operation == KeggOperation.LIST:
            if self.database:
                path_parts.append(str(self.database.value if isinstance(self.database, Enum) else self.database))
                # Special case for pathway/organism
                if self.database == KeggDatabase.PATHWAY and self.query:
                    path_parts.append(self.query)
                # Special case for brite/option
                elif self.database == KeggDatabase.BRITE and self.option:
                    path_parts.append(str(self.option.value if isinstance(self.option, Enum) else self.option))
            elif self.entries:
                path_parts.append("+".join(self.entries))

        elif self.operation == KeggOperation.FIND:
            if self.database and self.query:
                path_parts.append(str(self.database.value if isinstance(self.database, Enum) else self.database))
                path_parts.append(self.query)
                if self.option:
                    path_parts.append(str(self.option.value if isinstance(self.option, Enum) else self.option))

        elif self.operation == KeggOperation.GET:
            if self.entries or self.query:
                if self.entries:
                    path_parts.append("+".join(self.entries))
                elif self.query:
                    path_parts.append(self.query)

                if self.option:
                    path_parts.append(str(self.option.value if isinstance(self.option, Enum) else self.option))

        elif self.operation == KeggOperation.CONV:
            if self.target_db and self.source_db:
                path_parts.append(str(self.target_db.value if isinstance(self.target_db, Enum) else self.target_db))
                path_parts.append(str(self.source_db.value if isinstance(self.source_db, Enum) else self.source_db))
            elif self.target_db and self.entries:
                path_parts.append(str(self.target_db.value if isinstance(self.target_db, Enum) else self.target_db))
                path_parts.append("+".join(self.entries))

        elif self.operation == KeggOperation.LINK:
            if self.target_db and self.source_db:
                path_parts.append(str(self.target_db.value if isinstance(self.target_db, Enum) else self.target_db))
                path_parts.append(str(self.source_db.value if isinstance(self.source_db, Enum) else self.source_db))
                if self.option:
                    path_parts.append(str(self.option.value if isinstance(self.option, Enum) else self.option))
            elif self.target_db and self.entries:
                path_parts.append(str(self.target_db.value if isinstance(self.target_db, Enum) else self.target_db))
                path_parts.append("+".join(self.entries))
                if self.option:
                    path_parts.append(str(self.option.value if isinstance(self.option, Enum) else self.option))

        elif self.operation == KeggOperation.DDI and self.entries:
            path_parts.append("+".join(self.entries))

        return "/".join(path_parts)

    def execute(self) -> str:
        """Execute the API query based on the configuration.

        Performs the actual HTTP request to the KEGG API.
        """
        path = self.build_path()
        return execute_kegg_query(path)


@core_mcp.tool()
def query_kegg(
    operation: Annotated[
        KeggOperation, Field(description="The KEGG API operation to perform (info, list, find, get, conv, link, ddi)")
    ],
    database: Annotated[
        Optional[Union[KeggDatabase, KeggOutsideDb, str]],
        Field(description="The KEGG database to query (e.g., pathway, genes, compound) or organism code (e.g., hsa)"),
    ] = None,
    target_db: Annotated[
        Optional[Union[KeggDatabase, KeggOutsideDb, str]],
        Field(description="Target database for conversion or linking operations"),
    ] = None,
    source_db: Annotated[
        Optional[Union[KeggDatabase, KeggOutsideDb, str]],
        Field(description="Source database for conversion or linking operations"),
    ] = None,
    query: Annotated[
        Optional[str], Field(description="Query string for operations like FIND, or organism code for LIST")
    ] = None,
    option: Annotated[
        Optional[Union[KeggOption, KeggFindOption, KeggRdfFormat]],
        Field(description="Additional options like sequence formats, chemical formula search, etc."),
    ] = None,
    entries: Annotated[
        Optional[List[str]], Field(description="List of KEGG entry IDs (e.g., ['hsa:7157', 'hsa:00010'])")
    ] = None,
) -> str | dict:
    """Execute a KEGG API query.

    This function provides access to the KEGG API, allowing you to query biological data across
    pathways, genes, compounds, diseases, and more. The function can perform all KEGG API operations
    and accepts various parameters depending on the operation.

    When searching for genes in KEGG, you typically need KEGG IDs rather than gene symbols.
    Use the get_kegg_id_by_gene_symbol function first to convert gene symbols to KEGG IDs.

    Common operations:
    - info: Get database metadata (e.g., operation=info, database=PATHWAY)
    - list: List entries in a database (e.g., operation=list, database=PATHWAY, query="hsa")
    - get: Retrieve specific entries (e.g., operation=get, entries=["hsa:7157"])
    - find: Search for entries by keyword (e.g., operation=find, database=COMPOUND, query="glucose")
    - link: Find related entries (e.g., operation=link, target_db=PATHWAY, entries=["hsa:7157"])
    - conv: Convert between identifiers (e.g., operation=conv, target_db=NCBI_GENEID, entries=["hsa:7157"])

    Args:
        operation (KeggOperation): The KEGG operation to perform.
        database (KeggDatabase | KeggOutsideDb | str, optional): The database to query.
        target_db (KeggDatabase | KeggOutsideDb | str, optional): The target database for conversion.
        source_db (KeggDatabase | KeggOutsideDb | str, optional): The source database for conversion.
        query (str, optional): The query string for FIND or LIST operations.
        option (KeggOption | KeggFindOption | KeggRdfFormat, optional): Additional options for the operation.
        entries (List[str], optional): List of entries for GET or LINK operations.

    Returns:
        str | dict: The result of the KEGG query or an error message.

    Examples:
        # List human pathways
        >>> query_kegg(operation=KeggOperation.LIST, database=KeggDatabase.PATHWAY, query="hsa")

        # Get data for the glycolysis pathway
        >>> query_kegg(operation=KeggOperation.GET, entries=["hsa00010"])

        # Get data for the TP53 gene
        >>> query_kegg(operation=KeggOperation.GET, entries=["hsa:7157"])

        # Get amino acid sequence for TP53
        >>> query_kegg(operation=KeggOperation.GET, entries=["hsa:7157"], option=KeggOption.AASEQ)

        # Find compounds with formula C7H10O5
        >>> query_kegg(operation=KeggOperation.FIND, database=KeggDatabase.COMPOUND, query="C7H10O5", option="formula")

        # Find pathways related to TP53
        >>> query_kegg(operation=KeggOperation.LINK, target_db=KeggDatabase.PATHWAY, entries=["hsa:7157"])

        # Convert KEGG ID to NCBI Gene ID
        >>> query_kegg(operation=KeggOperation.CONV, target_db="ncbi-geneid", source_db="hsa:7157")

        # Get information about a specific pathway
        >>> query_kegg(operation=KeggOperation.GET, entries=["hsa00010"])

        # Get the compound ID for caffeine
        >>> query_kegg(operation=KeggOperation.FIND, database=KeggDatabase.COMPOUND, query="caffeine")

        # Get the drug ID for acetaminophen
        >>> query_kegg(operation=KeggOperation.FIND, database=KeggDatabase.DRUG, query="acetaminophen")

        # Check if two drugs interact (ibuprofen and aspirin)
        >>> query_kegg(operation=KeggOperation.DDI, entries=["dr:D00126", "dr:D00109"])
    """
    config = KeggConfig(
        operation=operation,
        database=database,
        target_db=target_db,
        source_db=source_db,
        query=query,
        option=option,
        entries=entries or [],
    )
    try:
        KeggConfig.model_validate(config)
    except ValueError as e:
        return {"error": f"Invalid configuration: {e}"}

    try:
        return config.execute()
    except Exception as e:
        return {"error": f"Failed to execute KEGG query: {e}"}
