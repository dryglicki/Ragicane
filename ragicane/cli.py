#!/usr/bin/env python3
import sys

import asyncio
from dataclasses import dataclass
import aiohttp
from argparse import ArgumentParser
from typing import List, Optional


@dataclass
class NOAAConfig:
    base_url: str = "https://api.weather.gov/stations"


class WeatherCLI:
    DESCRIPTION = "Ragicane: Fetch NOAA stations, then NHC PDFs."

    def __init__(self, config: NOAAConfig):
        self.config = config

    def c_to_f(self, celsius: float) -> float:
        """
        Convert Celsius to Fahrenheit
        """
        return celsius * 9.0 / 5.0 + 32.0

    async def fetch_observation(
        self, session: aiohttp.ClientSession, station: str
    ) -> Optional[List]:
        url = f"{self.config.base_url}/{station}/observations/latest"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    temp = data["properties"]["temperature"]["value"]
                    dwpt = data["properties"]["dewpoint"]["value"]
                    rhum = data["properties"]["relativeHumidity"]["value"]
                    return (temp, dwpt, rhum)
        except aiohttp.ClientResponseError as e:
            if e.status == 404:
                print(f"[ERROR] Station {station}: not found (404)", file=sys.stderr)
            else:
                print(f"[ERROR] Station {station}: HTTP {e.status}", file=sys.stderr)
        except Exception as e:
            # All other errors
            print(f"[ERROR] Station {station}: {e}", file=sys.stderr)
        return [None] * 3

    def parse_args(self):
        p = ArgumentParser(description=self.DESCRIPTION)
        p.add_argument(
            "-s",
            "--stations",
            nargs="+",
            default=["KLAL"],
            help="Station ID. Can be a list. Default: KJFK",
        )
        p.add_argument(
            "--c_to_f", action="store_true", help="Convert Celsius to Fahrenheit"
        )
        return p.parse_args()

    async def run(self):
        args = self.parse_args()
        stations = args.stations
        convert = args.c_to_f
        stations = [st.upper() for st in stations]
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_observation(session, station.upper()) for station in stations
            ]
            results = await asyncio.gather(*tasks)
        for station, (t, d, r) in zip(stations, results):
            if t is not None:
                unit = "˚C"
                rhunit = "%"
                if convert:
                    t = self.c_to_f(t)
                    if d is not None:
                        d = self.c_to_f(d)
                    else:
                        d = -99.0
                    unit = "˚F"
                if r is None:
                    r = -99.0
                print(
                    f"{station.upper()}: {t:03.1f} {unit}  {d:03.1f} {unit}  {r:0.2f} {rhunit}"
                )

def main():
    cfg = NOAAConfig()
    cli = WeatherCLI(cfg)
    asyncio.run(cli.run())

if __name__ == "__main__":
    main()
