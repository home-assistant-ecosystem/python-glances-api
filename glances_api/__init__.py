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
        version: int = 3,
        ssl: bool = False,
        verify_ssl: bool = True,
        username: str | None = None,
        password: str | None = None,
        httpx_client: httpx.AsyncClient | None = None,
    ):
        """Initialize the connection."""
        if version == 2:
            _LOGGER.warning(
                "Glances api older than v3 will not be supported in the next release."
            )

        schema = "https" if ssl else "http"
        self.url = f"{schema}://{host}:{port}/api/{version}"
        self.data: dict[str, Any] = {}
        self.plugins: list[str] = []
        self.values: dict[str, Any] | None = None
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.httpx_client = httpx_client
        self.version = version

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
                elif self.username is not None:
                    response = await client.get(
                        url, auth=(self.username, self.password)
                    )
                else:
                    raise ValueError("username and password must be provided.")
        except (httpx.ConnectError, httpx.TimeoutException) as err:
            raise exceptions.GlancesApiConnectionError(
                f"Connection to {url} failed"
            ) from err

        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise exceptions.GlancesApiAuthorizationError(
                "Please check your credentials"
            )

        if response.status_code != httpx.codes.OK:
            raise exceptions.GlancesApiNoDataAvailable(
                f"endpoint: '{endpoint}' is not valid"
            )
        try:
            _LOGGER.debug(response.json())
            if endpoint == "all":
                self.data = response.json()
            elif endpoint == "pluginslist":
                self.plugins = response.json()
        except TypeError as err:
            _LOGGER.error("Can not load data from Glances")
            raise exceptions.GlancesApiConnectionError(
                "Unable to get the data from Glances"
            ) from err

    async def get_metrics(self, element: str) -> None:
        """Get all the metrics for a monitored element."""
        await self.get_data("all")
        await self.get_data("pluginslist")

        if element in self.plugins:
            self.values = self.data[element]
        else:
            raise exceptions.GlancesApiError("Element data not available")

    async def get_ha_sensor_data(self) -> dict[str, Any]:
        """Create a dictionary with data for Home Assistant sensors."""
        await self.get_data("all")

        sensor_data: dict[str, Any] = {}

        if disks := self.data.get("fs"):
            sensor_data["fs"] = {}
            for disk in disks:
                disk_free = disk.get("free") or (disk["size"] - disk["used"])
                sensor_data["fs"][disk["mnt_point"]] = {
                    "disk_use": round(disk["used"] / 1024**3, 1),
                    "disk_use_percent": disk["percent"],
                    "disk_free": round(disk_free / 1024**3, 1),
                }
        if data := self.data.get("sensors"):
            sensor_data["sensors"] = {}
            for sensor in data:
                sensor_data["sensors"][sensor["label"]] = {
                    sensor["type"]: sensor["value"]
                }
        if data := self.data.get("mem"):
            sensor_data["mem"] = {
                "memory_use_percent": data["percent"],
                "memory_use": round(data["used"] / 1024**2, 1),
                "memory_free": round(data["free"] / 1024**2, 1),
            }
        if data := self.data.get("memswap"):
            sensor_data["memswap"] = {
                "swap_use_percent": data["percent"],
                "swap_use": round(data["used"] / 1024**3, 1),
                "swap_free": round(data["free"] / 1024**3, 1),
            }
        if data := self.data.get("load"):
            sensor_data["load"] = {
                "processor_load": data.get("min15"),
                "processor_load_1m": data.get("min1"),
                "processor_load_5m": data.get("min5"),
            }
        if data := self.data.get("processcount"):
            sensor_data["processcount"] = {
                "process_running": data["running"],
                "process_total": data["total"],
                "process_thread": data["thread"],
                "process_sleeping": data["sleeping"],
            }
        if data := self.data.get("quicklook"):
            sensor_data["cpu"] = {"cpu_use_percent": data["cpu"]}
        if data := self.data.get("percpu"):
            sensor_data["percpu"] = {}
            for cpu in data:
                sensor_data["percpu"][str(cpu["cpu_number"])] = {
                    "cpu_use_percent": cpu["total"]
                }
        if networks := self.data.get("network"):
            sensor_data["network"] = {}
            for network in networks:
                rx = tx = None
                if self.version <= 3:
                    time_since_update = network["time_since_update"]
                    if (rx_bytes := network.get("rx")) is not None:
                        rx = round(rx_bytes / time_since_update)
                    if (tx_bytes := network.get("tx")) is not None:
                        tx = round(tx_bytes / time_since_update)
                else:
                    # New network sensors in Glances v4
                    rx = network.get("bytes_recv_rate_per_sec")
                    tx = network.get("bytes_sent_rate_per_sec")
                sensor_data["network"][network["interface_name"]] = {
                    "is_up": network.get("is_up"),
                    "rx": rx,
                    "tx": tx,
                    "speed": round(network["speed"] / 1024**3, 1),
                }
        containers_data = None
        if self.version <= 3:
            # Glances v3 and earlier provide a dict, with containers inside a list in this dict
            # Key is "dockers" in 3.3 and before, and "containers" in 3.4
            data = self.data.get("dockers") or self.data.get("containers")
            containers_data = data.get("containers") if data else None
        else:
            # Glances v4 provides a list of containers
            containers_data = self.data.get("containers")
        if containers_data:
            sensor_data["containers"] = {}
            active_containers = [
                container
                for container in containers_data
                # "status" since Glance v4, "Status" in v3 and earlier
                if container.get("status") == "running"
                or container.get("Status") == "running"
            ]
            sensor_data["docker"] = {"docker_active": len(active_containers)}
            cpu_use = 0.0
            for container in active_containers:
                cpu_use += container["cpu"].get("total", 0)
            sensor_data["docker"]["docker_cpu_use"] = round(cpu_use, 1)
            mem_use = 0.0
            for container in active_containers:
                mem_use += container["memory"].get("usage", 0)
            sensor_data["docker"]["docker_memory_use"] = round(mem_use / 1024**2, 1)
            for container in active_containers:
                sensor_data["containers"][container["name"]] = {
                    "container_cpu_use": round(container["cpu"].get("total", 0), 1),
                    "container_memory_use": round(
                        container["memory"].get("usage", 0) / 1024**2, 1
                    ),
                }
        if data := self.data.get("raid"):
            sensor_data["raid"] = data
        if data := self.data.get("uptime"):
            sensor_data["uptime"] = data
        if data := self.data.get("gpu"):
            sensor_data["gpu"] = {}
            for sensor in data:
                sensor_data["gpu"][f"{sensor['name']} (GPU {sensor['gpu_id']})"] = {
                    "temperature": sensor.get("temperature", 0),
                    "mem": sensor.get("mem", 0),
                    "proc": sensor.get("proc", 0),
                    "fan_speed": sensor.get("fan_speed", 0),
                }
        if data := self.data.get("diskio"):
            sensor_data["diskio"] = {}
            for disk in data:
                time_since_update = disk["time_since_update"]
                sensor_data["diskio"][disk["disk_name"]] = {
                    "read": round(disk["read_bytes"] / time_since_update),
                    "write": round(disk["write_bytes"] / time_since_update),
                }
        return sensor_data
