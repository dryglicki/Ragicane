import pytest
from aioresponses import aioresponses
from ragicane_cli import WeatherCLI, NOAAConfig


@pytest.mark.asyncio
async def test_fetch_observation():
    mock = {"properties": {"temperature": {"value": 15.0}}}
    cfg = NOAAConfig(station="TEST", base_url="https://api.weather.gov/stations")
    cli = WeatherCLI(cfg)
    url = f"{cfg.base_url}/TEST/observations/latest"
    with aioresponses() as m:
        m.get(url, payload=mock)
        data = await cli.fetch_observation()
        assert data == mock


@pytest.mark.asyncio
async def test_run_output(monkeypatch, capsys):
    async def fake_fetch(self):
        return {"properties": {"temperature": {"value": 22.2}}}

    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
    import sys

    sys.argv = ["ragicane_cli.py", "--station", "abcd"]
    cfg = NOAAConfig()
    cli = WeatherCLI(cfg)
    await cli.run()
    out = capsys.readouterr().out
    assert "ABCD" in out and "22.2" in out
