"""Client to interact with the Glances API."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from . import exceptions

_LOGGER = logging.getLogger(__name__)


class Glances:
    """A class for handling the data retrieval."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 61208,
        version: int = 2,
        ssl: bool = False,
        verify_ssl: bool = True,
        username: str | None = None,
        password: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ):
        """Initialize the connection."""
        schema = "https" if ssl else "http"
        self.url = f"{schema}://{host}:{port}/api/{version}"
        self.data: dict[str, Any] = {}
        self.plugins: list[str] = []
        self.values: Any | None = None
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.httpx_client = httpx_client

    async def get_data(self, endpoint: str) -> None:
        """Retrieve the data."""
        url = f"{self.url}/{endpoint}"

        httpx_client = (
            self.httpx_client
            if self.httpx_client
            else httpx.AsyncClient(verify=self.verify_ssl)
        )

        try:
            async with httpx_client as client:
                if self.password is None:
                    response = await client.get(url)
                else:
                    response = await client.get(
                        url, auth=(self.username, self.password)
                    )
        except (httpx.ConnectError, httpx.TimeoutException):
            raise exceptions.GlancesApiConnectionError(f"Connection to {url} failed")

        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise exceptions.GlancesApiAuthorizationError(
                "Please check your credentials"
            )
        if response.status_code == httpx.codes.BAD_REQUEST:
            raise exceptions.GlancesApiNoDataAvailable(
                f"endpoint: '{endpoint}' is not valid"
            )
        if response.status_code == httpx.codes.OK:
            try:
                _LOGGER.debug(response.json())
                if endpoint == "all":
                    self.data = response.json()
                elif endpoint == "pluginslist":
                    self.plugins = response.json()
            except TypeError:
                _LOGGER.error("Can not load data from Glances")
                raise exceptions.GlancesApiConnectionError(
                    "Unable to get the data from Glances"
                )

    async def get_metrics(self, element: str) -> None:
        """Get all the metrics for a monitored element."""
        await self.get_data("all")
        await self.get_data("pluginslist")

        if element in self.plugins:
            self.values = self.data[element]
        else:
            raise exceptions.GlancesApiError("Element data not available")