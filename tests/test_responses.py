"""Test the interaction with the Glances API."""
import pytest
from glances_api import Glances
from glances_api.exceptions import GlancesApiNoDataAvailable
from pytest_httpx import HTTPXMock

PLUGINS_LIST_RESPONSE = [
    "alert",
    "amps",
    "cloud",
    "connections",
    "core",
    "cpu",
    "diskio",
    "docker",
    "folders",
    "fs",
]

RESPONSE = {
    "cpu": {
        "total": 10.6,
        "user": 7.6,
        "system": 2.1,
        "idle": 88.8,
        "nice": 0.0,
        "iowait": 0.6,
    },
    "diskio": [
        {
            "time_since_update": 1,
            "disk_name": "nvme0n1",
            "read_count": 12,
            "write_count": 466,
            "read_bytes": 184320,
            "write_bytes": 23863296,
            "key": "disk_name",
        },
    ],
    "system": {
        "os_name": "Linux",
        "hostname": "fedora-35",
        "platform": "64bit",
        "linux_distro": "Fedora Linux 35",
        "os_version": "5.15.6-200.fc35.x86_64",
        "hr_name": "Fedora Linux 35 64bit",
    },
    "uptime": "3 days, 10:25:20",
}


@pytest.mark.asyncio
async def test_non_existing_endpoint(httpx_mock: HTTPXMock):
    """Test a non-exisiting endpoint."""
    httpx_mock.add_response(status_code=400)

    client = Glances()
    with pytest.raises(GlancesApiNoDataAvailable):
        await client.get_data("some-data")
    
    assert not client.data


@pytest.mark.asyncio
async def test_plugins_list(httpx_mock: HTTPXMock):
    """Test the plugins list response."""
    httpx_mock.add_response(json=PLUGINS_LIST_RESPONSE)

    client = Glances()
    await client.get_data("pluginslist")

    assert len(client.plugins) == 10


@pytest.mark.asyncio
async def test_exisiting_endpoint(httpx_mock: HTTPXMock):
    """Test the a valid endpoint."""
    httpx_mock.add_response(json=RESPONSE)

    client = Glances()
    await client.get_metrics("cpu")

    assert client.values["total"] == 10.6
    assert client.values["system"] == 2.1
