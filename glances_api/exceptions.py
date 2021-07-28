"""Exceptions for the client."""


class GlancesApiError(Exception):
    """General GlancesApiError exception occurred."""

    pass

class GlancesApiConnectionError(GlancesApiError):
    """When a connection error is encountered."""

    pass
class GlancesApiAuthorizationError(GlancesApiError):
    """When a connection error is encountered."""

    pass

class GlancesApiNoDataAvailable(GlancesApiError):
    """When no data is available."""

    pass
