class AuthenticationError(Exception):
    """Base authentication error"""


class SessionNotFoundError(AuthenticationError):
    """Session not found in request"""


class InvalidSessionError(AuthenticationError):
    """Session validation failed"""


class StytchError(AuthenticationError):
    """Stytch API error"""
