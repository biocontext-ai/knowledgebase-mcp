from importlib.metadata import version

from biocontext_kb.main import run_app

__version__ = version("biocontext_kb")

__all__ = [
    "run_app",
]


if __name__ == "__main__":
    run_app()
