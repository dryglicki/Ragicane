#!/usr/bin/env python3
import asyncio
from dataclasses import dataclass
import aiohttp
from argparse import ArgumentParser


@dataclass
class NOAAConfig:
    station: str = "KJFK"
    base_url: str = "https://api.weather.gov/stations"


class WeatherCLI:

    DESCRIPTION = "Ragicane: Fetch NOAA stations, then NHC PDFs."

    def __init__(self, config: NOAAConfig):
        self.config = config

    async def fetch_observation(self):
        url = f"{self.config.base_url}/{self.config.station}/observations/latest"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                return await resp.json()

    def parse_args(self):
        p = ArgumentParser(description=self.DESCRIPTION)
        p.add_argument(
            "-s", "--station", default="KJFK", help="Station ID. Default: KJFK"
        )
        return p.parse_args()

    async def run(self):
        args = self.parse_args()
        self.config.station = args.station.upper()
        data = await self.fetch_observation()
        temp = data["properties"]["temperature"]["value"]
        print(f"{self.config.station}: {temp:0.1f} degC")


if __name__ == "__main__":
    cfg = NOAAConfig()
    cli = WeatherCLI(cfg)
    asyncio.run(cli.run())
