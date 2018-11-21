"""Client to interact with the Glances API."""
import asyncio
import logging

import aiohttp
import async_timeout

from . import exceptions

_LOGGER = logging.getLogger(__name__)
_RESOURCE = '{schema}://{host}:{port}/api/{version}'


class Glances(object):
    """A class for handling the data retrieval."""

    def __init__(self, loop, session, host='localhost', port=61208, version=2,
                 ssl=False, username=None, password=None):
        """Initialize the connection."""
        schema = 'https' if ssl else 'http'
        self._loop = loop
        self._session = session
        self.url = _RESOURCE.format(schema=schema, host=host, port=port,
                                    version=version)
        self.data = None
        self.values = None
        self.plugins = None
        self.username = username
        self.password = password

    async def get_data(self):
        """Retrieve the data."""
        url = '{}/{}'.format(self.url, 'all')

        try:
            with async_timeout.timeout(5, loop=self._loop):
                if self.password is None:
                    response = await self._session.get(url)
                else:
                    auth = aiohttp.BasicAuth(self.username, self.password)
                    response = await self._session.get(url, auth=auth)

            _LOGGER.debug("Response from Glances API: %s", response.status)
            self.data = await response.json()
            _LOGGER.debug(self.data)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Can not load data from Glances API")
            raise exceptions.GlancesApiConnectionError()

    async def get_metrics(self, element):
        """Get all the metrics for a monitored element."""
        await self.get_data()
        await self.get_plugins()

        if element in self.plugins:
            self.values = self.data[element]
        else:
            raise exceptions.GlancesApiError("Element data not available")

    async def get_plugins(self):
        """Retrieve the available plugins."""
        url = '{}/{}'.format(self.url, 'pluginslist')

        try:
            with async_timeout.timeout(5, loop=self._loop):
                if self.password is None:
                    response = await self._session.get(url)
                else:
                    auth = aiohttp.BasicAuth(self.username, self.password)
                    response = await self._session.get(url, auth=auth)

            _LOGGER.debug("Response from Glances API: %s", response.status)
            self.plugins = await response.json()
            _LOGGER.debug(self.plugins)
        except (asyncio.TimeoutError, aiohttp.ClientError):
            _LOGGER.error("Can not load plugins from Glances API")
            raise exceptions.GlancesApiConnectionError()
