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
    "docker": {
        "containers": [
            {
                "key": "name",
                "name": "container1",
                "Status": "running",
                "cpu": {"total": 50.94973493230174},
                "cpu_percent": 50.94973493230174,
                "memory": {
                    "usage": 1120321536,
                    "limit": 3976318976,
                    "rss": 480641024,
                    "cache": 580915200,
                    "max_usage": 1309597696,
                },
                "memory_usage": 539406336,
            },
            {
                "key": "name",
                "name": "container2",
                "Status": "running",
                "cpu": {"total": 26.23567931034483},
                "cpu_percent": 26.23567931034483,
                "memory": {
                    "usage": 85139456,
                    "limit": 3976318976,
                    "rss": 33677312,
                    "cache": 35012608,
                    "max_usage": 87650304,
                },
                "memory_usage": 50126848,
            },
        ]
    },
    "fs": [
        {
            "device_name": "/dev/sda8",
            "fs_type": "ext4",
            "mnt_point": "/ssl",
            "size": 511320748032,
            "used": 32910458880,
            "free": 457917374464,
            "percent": 6.7,
            "key": "mnt_point",
        },
        {
            "device_name": "/dev/sda8",
            "fs_type": "ext4",
            "mnt_point": "/media",
            "size": 511320748032,
            "used": 32910458880,
            "free": 457917374464,
            "percent": 6.7,
            "key": "mnt_point",
        },
    ],
    "mem": {
        "total": 3976318976,
        "available": 2878337024,
        "percent": 27.6,
        "used": 1097981952,
        "free": 2878337024,
        "active": 567971840,
        "inactive": 1679704064,
        "buffers": 149807104,
        "cached": 1334816768,
        "shared": 1499136,
    },
    "sensors": [
        {
            "label": "cpu_thermal 1",
            "value": 59,
            "warning": None,
            "critical": None,
            "unit": "C",
            "type": "temperature_core",
            "key": "label",
        }
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

HA_SENSOR_DATA = {
    "fs": {
        "/ssl": {"disk_use": 30.7, "disk_use_percent": 6.7, "disk_free": 426.5},
        "/media": {"disk_use": 30.7, "disk_use_percent": 6.7, "disk_free": 426.5},
    },
    "sensors": {"cpu_thermal 1": {"temperature_core": 59}},
    "mem": {
        "memory_use_percent": 27.6,
        "memory_use": 1047.1,
        "memory_free": 2745.0,
    },
    "docker": {"docker_active": 2, "docker_cpu_use": 77.2, "docker_memory_use": 1149.6},
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


@pytest.mark.asyncio
async def test_ha_sensor_data(httpx_mock: HTTPXMock):
    """Test the return value for ha sensors."""
    httpx_mock.add_response(json=RESPONSE)

    client = Glances()
    result = await client.get_ha_sensor_data()

    assert result == HA_SENSOR_DATA

@pytest.mark.asyncio
async def test_ha_sensor_data_with_incomplete_container_information(httpx_mock: HTTPXMock):
    """Test the return value for ha sensors when container memory and cpu data is not exposed by glances."""
    TEST_RESPONSE = RESPONSE
    del TEST_RESPONSE["docker"]["containers"][0]["memory"]["usage"]
    del TEST_RESPONSE["docker"]["containers"][0]["cpu"]["total"]
    del TEST_RESPONSE["docker"]["containers"][1]["memory"]["usage"]
    del TEST_RESPONSE["docker"]["containers"][1]["cpu"]["total"]

    TEST_HA_SENSOR_DATA = HA_SENSOR_DATA
    TEST_HA_SENSOR_DATA["docker"]["docker_memory_use"] = 0
    TEST_HA_SENSOR_DATA["docker"]["docker_cpu_use"] = 0

    httpx_mock.add_response(json=TEST_RESPONSE)

    client = Glances()
    result = await client.get_ha_sensor_data()

    assert result == TEST_HA_SENSOR_DATA
