class AllenNeuroMCPError(Exception):
    """Base exception for expected project errors."""


class CellNotFoundError(AllenNeuroMCPError):
    """Raised when a requested Allen Cell Types specimen cannot be found."""


class InvalidQueryError(AllenNeuroMCPError):
    """Raised when a query is invalid or unsafe."""

class DependencyUnavailableError(AllenNeuroMCPError):
    """Raised when an optional dependency like AllenSDK is not installed."""