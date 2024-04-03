"""Test the interaction with the Glances API."""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from glances_api import Glances
from glances_api.exceptions import GlancesApiNoDataAvailable

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

RESPONSE: dict[str, Any] = {
    "cpu": {
        "total": 10.6,
        "user": 7.6,
        "system": 2.1,
        "idle": 88.8,
        "nice": 0.0,
        "iowait": 0.6,
    },
    "percpu": [
        {
            "key": "cpu_number",
            "cpu_number": 0,
            "total": 22.1,
            "user": 7.6,
            "system": 12.4,
            "idle": 77.9,
            "nice": 0.0,
            "iowait": 0.2,
            "irq": 0.0,
            "softirq": 1.8,
            "steal": 0.0,
            "guest": 0.0,
            "guest_nice": 0.0,
        },
        {
            "key": "cpu_number",
            "cpu_number": 1,
            "total": 17.2,
            "user": 8.7,
            "system": 7.8,
            "idle": 82.8,
            "nice": 0.0,
            "iowait": 0.4,
            "irq": 0.0,
            "softirq": 0.3,
            "steal": 0.0,
            "guest": 0.0,
            "guest_nice": 0.0,
        },
    ],
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
    "containers": {
        "version": {},
        "version_podman": {},
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
        ],
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
    "gpu": [
        {
            "key": "gpu_id",
            "gpu_id": 0,
            "name": "NVIDIA GeForce RTX 4080",
            "mem": 13.333489176233513,
            "proc": 12,
            "temperature": 38,
            "fan_speed": 30,
        },
        {
            "key": "gpu_id",
            "gpu_id": 1,
            "name": "NVIDIA GeForce RTX 3080",
            "mem": 8.41064453125,
            "proc": 26,
            "temperature": 51,
            "fan_speed": 0,
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
    "network": [
        {
            "cumulative_cx": 19027046,
            "cumulative_rx": 9513523,
            "cumulative_tx": 9513523,
            "cx": 23770,
            "interface_name": "lo",
            "is_up": True,
            "key": "interface_name",
            "rx": 11885,
            "speed": 0,
            "time_since_update": 1.55433297157288,
            "tx": 11885,
        },
        {
            "cumulative_cx": 0,
            "cumulative_rx": 0,
            "cumulative_tx": 0,
            "cx": 0,
            "interface_name": "bond0",
            "is_up": False,
            "key": "interface_name",
            "rx": 0,
            "speed": 68718428160,
            "time_since_update": 1.55433297157288,
            "tx": 0,
        },
        {
            "cumulative_cx": 0,
            "cumulative_rx": 0,
            "cumulative_tx": 0,
            "cx": 0,
            "interface_name": "dummy0",
            "is_up": False,
            "key": "interface_name",
            "rx": 0,
            "speed": 0,
            "time_since_update": 1.55433297157288,
            "tx": 0,
        },
        {
            "cumulative_cx": 704585,
            "cumulative_rx": 518329,
            "cumulative_tx": 186256,
            "cx": 15463,
            "interface_name": "eth0",
            "is_up": True,
            "key": "interface_name",
            "rx": 6144,
            "speed": 10485760000,
            "time_since_update": 1.55433297157288,
            "tx": 9319,
        },
        {
            "cumulative_cx": 0,
            "cumulative_rx": 0,
            "cumulative_tx": 0,
            "cx": 0,
            "interface_name": "tunl0",
            "is_up": False,
            "key": "interface_name",
            "rx": 0,
            "speed": 0,
            "time_since_update": 1.55433297157288,
            "tx": 0,
        },
        {
            "cumulative_cx": 0,
            "cumulative_rx": 0,
            "cumulative_tx": 0,
            "cx": 0,
            "interface_name": "sit0",
            "is_up": False,
            "key": "interface_name",
            "rx": 0,
            "speed": 0,
            "time_since_update": 1.55433297157288,
            "tx": 0,
        },
    ],
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

HA_SENSOR_DATA: dict[str, Any] = {
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
    "network": {
        "lo": {"is_up": True, "rx": 11.6, "tx": 11.6, "speed": 0.0},
        "bond0": {"is_up": False, "rx": 0.0, "tx": 0.0, "speed": 64.0},
        "dummy0": {"is_up": False, "rx": 0.0, "tx": 0.0, "speed": 0.0},
        "eth0": {"is_up": True, "rx": 6.0, "tx": 9.1, "speed": 9.8},
        "tunl0": {"is_up": False, "rx": 0.0, "tx": 0.0, "speed": 0.0},
        "sit0": {"is_up": False, "rx": 0.0, "tx": 0.0, "speed": 0.0},
    },
    "docker": {"docker_active": 2, "docker_cpu_use": 77.2, "docker_memory_use": 1149.6},
    "uptime": "3 days, 10:25:20",
    "percpu": {"0": {"cpu_use_percent": 22.1}, "1": {"cpu_use_percent": 17.2}},
    "gpu": {
        "NVIDIA GeForce RTX 4080 (GPU 0)": {
            "mem": 13.333489176233513,
            "proc": 12,
            "temperature": 38,
            "fan_speed": 30,
        },
        "NVIDIA GeForce RTX 3080 (GPU 1)": {
            "mem": 8.41064453125,
            "proc": 26,
            "temperature": 51,
            "fan_speed": 0,
        },
    },
}


@pytest.mark.asyncio
async def test_non_existing_endpoint(httpx_mock: HTTPXMock) -> None:
    """Test a non-exisiting endpoint."""
    httpx_mock.add_response(status_code=400)

    client = Glances()
    with pytest.raises(GlancesApiNoDataAvailable):
        await client.get_data("some-data")

    assert not client.data


@pytest.mark.asyncio
async def test_plugins_list(httpx_mock: HTTPXMock) -> None:
    """Test the plugins list response."""
    httpx_mock.add_response(json=PLUGINS_LIST_RESPONSE)

    client = Glances()
    await client.get_data("pluginslist")

    assert len(client.plugins) == 10


@pytest.mark.asyncio
async def test_exisiting_endpoint(httpx_mock: HTTPXMock) -> None:
    """Test the a valid endpoint."""
    httpx_mock.add_response(json=RESPONSE)

    client = Glances()
    await client.get_metrics("cpu")
    assert client.values
    assert client.values["total"] == 10.6
    assert client.values["system"] == 2.1


@pytest.mark.asyncio
async def test_ha_sensor_data(httpx_mock: HTTPXMock) -> None:
    """Test the return value for ha sensors."""
    httpx_mock.add_response(json=RESPONSE)

    client = Glances()
    result = await client.get_ha_sensor_data()

    assert result == HA_SENSOR_DATA


@pytest.mark.asyncio
async def test_ha_sensor_data_with_incomplete_container_information(
    httpx_mock: HTTPXMock,
) -> None:
    """Test the return value for ha sensors when some data is not exposed."""
    response = RESPONSE.copy()
    del response["containers"]["containers"][0]["memory"]["usage"]
    del response["containers"]["containers"][0]["cpu"]["total"]
    del response["containers"]["containers"][1]["memory"]["usage"]
    del response["containers"]["containers"][1]["cpu"]["total"]

    ha_sensor_data = HA_SENSOR_DATA.copy()
    ha_sensor_data["docker"]["docker_memory_use"] = 0
    ha_sensor_data["docker"]["docker_cpu_use"] = 0

    httpx_mock.add_response(json=response)

    client = Glances()
    result = await client.get_ha_sensor_data()

    assert result == ha_sensor_data
