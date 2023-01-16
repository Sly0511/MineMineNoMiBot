from .logger import Logger
from .tree import Tree


def chunks(l, n):
    """Yield successive n-sized chunks from list."""
    for i in range(0, len(l), n):
        yield l[i : i + n]
