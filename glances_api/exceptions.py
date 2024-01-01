"""Exceptions for the client."""


class GlancesApiError(Exception):
    """General GlancesApiError exception occurred."""


class GlancesApiConnectionError(GlancesApiError):
    """When a connection error is encountered."""


class GlancesApiAuthorizationError(GlancesApiError):
    """When a connection error is encountered."""


class GlancesApiNoDataAvailable(GlancesApiError):
    """When no data is available."""
