"""
Copyright (c) 2017-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""


class GlancesApiError(Exception):
    """General GlancesApiErrorError exception occurred."""

    pass


class GlancesApiConnectionError(GlancesApiError):
    """When a connection error is encountered."""

    pass


class GlancesApiNoDataAvailable(GlancesApiError):
    """When no data is available."""

    pass
