import pytest
import aiohttp
import argparse
from aioresponses import aioresponses

from ragicane_cli import WeatherCLI, NOAAConfig


@pytest.mark.asyncio
async def test_fetch_observation_success():
    # Prepare a full mock with temperature, dewpoint, and relative humidity
    mock_payload = {
        "properties": {
            "temperature": {"value": 15.0},
            "dewpoint": {"value": 10.0},
            "relativeHumidity": {"value": 55.0},
        }
    }
    cfg = NOAAConfig()
    cli = WeatherCLI(cfg)
    url = f"{cfg.base_url}/TEST/observations/latest"

    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(url, payload=mock_payload)
            result = await cli.fetch_observation(session, "TEST")
            assert result == (15.0, 10.0, 55.0)


@pytest.mark.asyncio
async def test_fetch_observation_not_found():
    cfg = NOAAConfig()
    cli = WeatherCLI(cfg)
    url = f"{cfg.base_url}/NO_SUCH/observations/latest"

    async with aiohttp.ClientSession() as session:
        with aioresponses() as m:
            m.get(url, status=404)
            result = await cli.fetch_observation(session, "NO_SUCH")
            assert tuple(result) == (None, None, None)


@pytest.mark.asyncio
async def test_run_output_celsius(monkeypatch, capsys):
    # Simulate CLI args: one station, no conversion
    args = argparse.Namespace(stations=["abcd"], c_to_f=False)
    monkeypatch.setattr(WeatherCLI, "parse_args", lambda self: args)

    # Fake fetch_observation to return known tuple
    async def fake_fetch(self, session, station):
        return (12.3, 6.7, 90.12)

    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)

    cli = WeatherCLI(NOAAConfig())
    await cli.run()

    out = capsys.readouterr().out
    # Expect unpadded fields and °C units
    assert "ABCD: 12.3 ˚C  6.7 ˚C  90.12 %" in out


@pytest.mark.asyncio
async def test_run_output_fahrenheit(monkeypatch, capsys):
    # Simulate CLI args: one station, with conversion flag
    args = argparse.Namespace(stations=["abcd"], c_to_f=True)
    monkeypatch.setattr(WeatherCLI, "parse_args", lambda self: args)

    # Fake fetch_observation: returns 0°C for temp, None for dewpoint & RH
    async def fake_fetch(self, session, station):
        return (0.0, None, None)

    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)

    cli = WeatherCLI(NOAAConfig())
    await cli.run()

    out = capsys.readouterr().out
    # 0°C → 32°F, missing dewpoint → -99.0, missing RH → -99.00
    assert "ABCD: 32.0 ˚F  -99.0 ˚F  -99.00 %" in out
