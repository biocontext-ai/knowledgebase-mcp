def slugify(name: str) -> str:
    """Slugify a name by replacing spaces with underscores and converting to lowercase.

    Allow only alphanumeric characters and underscores.
    """
    return "".join(c if c.isalnum() else "-" for c in name.strip().replace(" ", "-").lower())
