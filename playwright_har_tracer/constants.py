import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


HAR_VERSION: str = "1.2"
CREATOR_NAME: str = "playwright-har-tracer"
CREATOR_VERSION: str = __version__

FALLBACK_HTTP_VERSION: str = "HTTP/1.1"
