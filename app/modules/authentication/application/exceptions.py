class AuthenticationError(Exception):
    """Base error for the authentication module."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when username/password do not match."""


class ApiKeyNotFoundError(AuthenticationError):
    """Raised when an API key cannot be found."""

