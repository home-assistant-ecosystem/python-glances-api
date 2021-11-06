"""Test the interaction with the currencylayer API."""
import pytest
from pytest_httpx import HTTPXMock

from glances_api import Glances
import httpx


@pytest.mark.asyncio
async def test_timeout(httpx_mock: HTTPXMock):
    """Test if the connection is hitting the timeout."""

    def raise_timeout(request, extensions: dict):
        """Set the timeout for the requests."""
        raise httpx.ReadTimeout(
            f"Unable to read within {extensions['timeout']}", request=request
        )

    httpx_mock.add_callback(raise_timeout)

    with pytest.raises(httpx.ReadTimeout):
        client = Glances()
        await client.get_metrics("mem")
