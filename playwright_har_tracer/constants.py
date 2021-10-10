import importlib.metadata

NAME: str = "playwright-har-tracer"

__version__ = importlib.metadata.version(NAME)

HAR_VERSION: str = "1.2"
CREATOR_NAME: str = NAME
CREATOR_VERSION: str = __version__

FALLBACK_HTTP_VERSION: str = "HTTP/1.1"
