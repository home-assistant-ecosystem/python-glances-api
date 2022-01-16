"""Client to interact with the Glances API."""
import asyncio
import logging

import httpx

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE = "{schema}://{host}:{port}/api/{version}"


class Glances(object):
    """A class for handling the data retrieval."""

    def __init__(
        self,
        host="localhost",
        port=61208,
        version=2,
        ssl=False,
        verify_ssl=True,
        username=None,
        password=None,
        httpx_client=None,
    ):
        """Initialize the connection."""
        schema = "https" if ssl else "http"
        self.url = _RESOURCE.format(
            schema=schema, host=host, port=port, version=version
        )
        self.plugins = None
        self.values = None
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.httpx_client = httpx_client

    async def get_data(self, endpoint):
        """Retrieve the data."""
        url = "{}/{}".format(self.url, endpoint)

        httpx_client = (
            self.httpx_client
            if self.httpx_client
            else httpx.AsyncClient(verify=self.verify_ssl)
        )

        try:
            async with httpx_client as client:
                if self.password is None:
                    response = await client.get(str(url))
                else:
                    response = await client.get(
                        str(url), auth=(self.username, self.password)
                    )
        except httpx.ConnectError:
            raise exceptions.GlancesApiConnectionError(f"Connection to {url} failed")

        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise exceptions.GlancesApiAuthorizationError(
                "Please check your credentials"
            )

        if response.status_code == httpx.codes.OK:
            try:
                _LOGGER.debug(response.json())
                if endpoint == "all":
                    self.data = response.json()
                if endpoint == "pluginslist":
                    self.plugins = response.json()
            except TypeError:
                _LOGGER.error("Can not load data from Glances")
                raise exceptions.GlancesApiConnectionError(
                    "Unable to get the data from Glances"
                )

    async def get_metrics(self, element):
        """Get all the metrics for a monitored element."""
        await self.get_data("all")
        await self.get_data("pluginslist")

        if element in self.plugins:
            self.values = self.data[element]
        else:
            raise exceptions.GlancesApiError("Element data not available")
