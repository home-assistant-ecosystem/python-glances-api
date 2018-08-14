"""
Copyright (c) 2017-2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""
import asyncio

import aiohttp

from glances_api import Glances

HOST = '127.0.0.1'


async def main():
    """The main part of the example script."""
    async with aiohttp.ClientSession() as session:
        data = Glances(loop, session)

        # Get the metrics for the memory
        await data.get_metrics('mem')

        # Print the values
        print("Memory values:", data.values)

        # Get the metrics about the disks
        await data.get_metrics('diskio')

        # Print the values
        print("Disk values:", data.values)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
