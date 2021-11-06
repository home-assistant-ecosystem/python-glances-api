"""Sample script to use the Python API client for Glances."""
import asyncio

from glances_api import Glances

HOST = "127.0.0.1"
VERSION = 3


async def main():
    """The main part of the example script."""
    data = Glances(version=VERSION)

    # Get the metrics for the memory
    await data.get_metrics("mem")

    # Print the values
    print("Memory values:", data.values)

    # Get the metrics about the disks
    await data.get_metrics("diskio")

    # Print the values
    print("Disk values:", data.values)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
