"""Shared exception hierarchy used across layers."""


class DomainError(Exception):
    """Raised when a domain rule is violated."""


class ApplicationError(Exception):
    """Raised by use cases when an operation fails."""

