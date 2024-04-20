from importlib import metadata

__version__ = metadata.version("list-publications")

from . import query

__all__ = ["query"]
