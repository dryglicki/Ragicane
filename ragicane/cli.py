#!/usr/bin/env python3
import sys

import asyncio
from dataclasses import dataclass
import aiohttp
from argparse import ArgumentParser
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from ragicane.ingest_pipeline import ingest_directory

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
        self,
        session: aiohttp.ClientSession,
        station: str
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

#   def parse_args(self):
#       p = ArgumentParser(description=self.DESCRIPTION)
#       p.add_argument(
#           "-s",
#           "--stations",
#           nargs="+",
#           default=["KLAL"],
#           help="Station ID. Can be a list. Default: KJFK",
#       )
#       p.add_argument(
#           "--c_to_f", action="store_true", help="Convert Celsius to Fahrenheit"
#       )
#       return p.parse_args()

    async def run(self, stations: List[str], convert:bool):
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
                else:
                    d = d if d is not None else -99.0
                r = r if r is not None else -99.0
                print(
                    f"{station.upper()}: {t:03.1f} {unit}  {d:03.1f} {unit}  {r:0.2f} {rhunit}"
                )
            else:
                print(f"Could not find station: {station.upper()}")

def main():
    parser = ArgumentParser(
            prog = "ragicane",
            description = "Ragicane CLI - Fetch NOAA stations of ingest PDF reports."
            )

    subparsers = parser.add_subparsers(dest = "command", required = True)

    ###### ---- "fetch" parser
    fetch_parser = subparsers.add_parser(
            'fetch', help = 'Fetch latest NOAA observations from one or more stations.')

    fetch_parser.add_argument(
            "-s",
            "--stations",
            nargs = "+",
            default = ['KTPA'],
            help = 'Station IDs. Provide one or more. Default: KTPA.'
            )

    fetch_parser.add_argument(
            '--c_to_f',
            action = 'store_true',
            help = 'Convert Celsius to Fahrenheit where available.'
            )

    ###### ingest-pdf parser
    ingest_parser = subparsers.add_parser(
            "ingest-pdf", help = 'Ingest all post-season PDF reports in a directory.'
            )

    ingest_parser.add_argument(
            "pdf_dir", help = "Path to folder containing PDF files."
            )

    args = parser.parse_args()

    print(f"The current date is {datetime.now().strftime('%Y %B %d: %H%M UTC')}")
    if args.command == 'fetch':

        stations = [ st.upper() for st in args.stations ]
        convert = args.c_to_f


        cfg = NOAAConfig()
        cli = WeatherCLI(cfg)
        asyncio.run(cli.run(stations, convert))

    elif args.command == 'ingest-pdf':
        pdf_folder = Path(args.pdf_dir)

        chunks_map = asyncio.run(ingest_directory(pdf_folder))

        for p, c in chunks_map.items():
            print(f"{p.name}: {len(c)} chunks")
    
    return

if __name__ == "__main__":
    main()
