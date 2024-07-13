from importlib.metadata import version, PackageNotFoundError

# Official PEP 396
try:
    __version__ = version('toolagent')
except PackageNotFoundError:
    __version__ = "unknown version"