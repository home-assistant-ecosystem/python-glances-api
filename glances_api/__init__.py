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

        httpx_client: Any = (
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

    async def get_ha_sensor_data(self) -> dict[str, Any] | None:
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
                "processor_load": data.get("min15")
                or self.data["cpu"]["total"]  # to be checked
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
        if "docker" in self.data and (data := self.data["docker"].get("containers")):
            active_containers = [
                container for container in data if container["Status"] == "running"
            ]
            sensor_data["docker"] = {"docker_active": len(active_containers)}
            cpu_use = 0.0
            for container in active_containers:
                cpu_use += container["cpu"]["total"]
            sensor_data["docker"]["docker_cpu_use"] = round(cpu_use, 1)
            mem_use = 0.0
            for container in active_containers:
                mem_use += container["memory"]["usage"]
            sensor_data["docker"]["docker_memory_use"] = round(mem_use / 1024**2, 1)
        if data := self.data.get("raid"):
            sensor_data["raid"] = data
        return sensor_data
