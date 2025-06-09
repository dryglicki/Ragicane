import sys
from pathlib import Path

from ragicane.cli import main as cli_main
from ragicane.cli import WeatherCLI
import ragicane.cli as cli_mod

# @pytest.mark.asyncio
# async def test_fetch_subcommand_celsius(monkeypatch, capsys):
#    """
#    Simulate `ragicane fetch -s abcd` where fetch_observation returns (temp, dewpoint, humidity).
#    Expect printed line in °C.
#    """
#    # 1) Monkey‐patch WeatherCLI.fetch_observation to return a known tuple
#    async def fake_fetch(self, session, station):
#        # pretend station exists with 15°C, 5°C dewpoint, 80% RH
#        return (15.0, 5.0, 80.0)
#
#    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
#
#    # 2) Simulate CLI args (override sys.argv)
#    monkeypatch.setattr(sys, "argv", ["ragicane", "fetch", "-s", "abcd"])
#
#    # 3) Run the CLI (this will print to stdout)
#    cli_main()
#
#    # 4) Capture stdout
#    out = capsys.readouterr().out
#
#    # Station should be uppercased, no conversion flag → outputs °C
#    # Format: "ABCD: 15.0 ˚C  5.0 ˚C  80.00 %"
#    assert "ABCD: 15.0 ˚C  5.0 ˚C  80.00 %" in out


def test_fetch_subcommand_celsius(monkeypatch, capsys):
    # Stub out WeatherCLI.fetch_observation
    async def fake_fetch(self, session, station):
        return (15.0, 5.0, 80.0)

    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
    # Simulate: ragicane fetch -s abcd
    monkeypatch.setattr(sys, "argv", ["ragicane", "fetch", "-s", "abcd"])

    cli_main()

    out = capsys.readouterr().out
    assert "ABCD: 15.0 ˚C  5.0 ˚C  80.00 %" in out


def test_fetch_subcommand_fahrenheit(monkeypatch, capsys):
    async def fake_fetch(self, session, station):
        return (0.0, None, None)

    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
    # Simulate: ragicane fetch -s wxyz --c_to_f
    monkeypatch.setattr(sys, "argv", ["ragicane", "fetch", "-s", "wxyz", "--c_to_f"])

    cli_main()

    out = capsys.readouterr().out
    assert "WXYZ: 32.0 ˚F  -99.0 ˚F  -99.00 %" in out


def test_ingest_pdf_subcommand(monkeypatch, capsys):
    """
    Simulate `ragicane ingest-pdf /some/dir` by monkey-patching cli_mod.ingest_directory
    to return a fake mapping. Expect printed summary.
    """
    fake_path = Path("/fake/path/a.pdf")
    fake_map = {fake_path: ["chunk1", "chunk2", "chunk3"]}

    async def fake_ingest(dir_path):
        return fake_map

    # Monkey-patch the ingest_directory that cli.py uses
    monkeypatch.setattr(cli_mod, "ingest_directory", fake_ingest)
    monkeypatch.setattr(sys, "argv", ["ragicane", "ingest-pdf", "/does/not/matter"])

    cli_main()

    out = capsys.readouterr().out
    assert "a.pdf: 3 chunks" in out


# @pytest.mark.asyncio
# async def test_fetch_subcommand_fahrenheit(monkeypatch, capsys):
#    """
#    Simulate `ragicane fetch -s wxyz --c_to_f` where fetch_observation returns
#    (0.0, None, None). Expect 32.0 ˚F, -99.0 ˚F, -99.00 %.
#    """
#    async def fake_fetch(self, session, station):
#        return (0.0, None, None)  # 0°C, missing dewpoint & RH
#
#    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
#    monkeypatch.setattr(sys, "argv", ["ragicane", "fetch", "-s", "wxyz", "--c_to_f"])
#
#    cli_main()
#    out = capsys.readouterr().out
#
#    # 0°C → 32°F; dewpoint None → -99.0; RH None → -99.00
#    assert "WXYZ: 32.0 ˚F  -99.0 ˚F  -99.00 %" in out
#
# def test_ingest_pdf_subcommand(monkeypatch, capsys):
#    """
#    Simulate `ragicane ingest-pdf /some/dir` by monkey-patching ingest_directory
#    to return {Path("/a.pdf"): ["chunk1", "chunk2"]}. Expect printed line.
#    """
#    fake_path = Path("/fake/path/a.pdf")
#    fake_map = {fake_path: ["chunk1", "chunk2", "chunk3"]}
#
#    async def fake_ingest(dir_path):
#        return fake_map
#
#    # Monkey-patch ingest_directory in ragicane.ingest_pipeline
#    import ragicane.ingest_pipeline as ip_mod
#    monkeypatch.setattr(ip_mod, "ingest_directory", fake_ingest)
#
#    # Override sys.argv
#    monkeypatch.setattr(sys, "argv", ["ragicane", "ingest-pdf", "/does/not/matter"])
#
#    cli_main()
#    out = capsys.readouterr().out
#
#    assert "a.pdf: 3 chunks" in out


# @pytest.mark.asyncio
# async def test_fetch_observation_not_found():
#    cfg = NOAAConfig()
#    cli = WeatherCLI(cfg)
#    url = f"{cfg.base_url}/NO_SUCH/observations/latest"
#
#    async with aiohttp.ClientSession() as session:
#        with aioresponses() as m:
#            m.get(url, status=404)
#            result = await cli.fetch_observation(session, "NO_SUCH")
#            assert tuple(result) == (None, None, None)
#
#
# @pytest.mark.asyncio
# async def test_run_output_celsius(monkeypatch, capsys):
#    # Simulate CLI args: one station, no conversion
#    args = argparse.Namespace(stations=["abcd"], c_to_f=False)
#    monkeypatch.setattr(WeatherCLI, "parse_args", lambda self: args)
#
#    # Fake fetch_observation to return known tuple
#    async def fake_fetch(self, session, station):
#        return (12.3, 6.7, 90.12)
#
#    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
#
#    cli = WeatherCLI(NOAAConfig())
#    await cli.run()
#
#    out = capsys.readouterr().out
#    # Expect unpadded fields and °C units
#    assert "ABCD: 12.3 ˚C  6.7 ˚C  90.12 %" in out
#
#
# @pytest.mark.asyncio
# async def test_run_output_fahrenheit(monkeypatch, capsys):
#    # Simulate CLI args: one station, with conversion flag
#    args = argparse.Namespace(stations=["abcd"], c_to_f=True)
#    monkeypatch.setattr(WeatherCLI, "parse_args", lambda self: args)
#
#    # Fake fetch_observation: returns 0°C for temp, None for dewpoint & RH
#    async def fake_fetch(self, session, station):
#        return (0.0, None, None)
#
#    monkeypatch.setattr(WeatherCLI, "fetch_observation", fake_fetch)
#
#    cli = WeatherCLI(NOAAConfig())
#    await cli.run()
#
#    out = capsys.readouterr().out
#    # 0°C → 32°F, missing dewpoint → -99.0, missing RH → -99.00
#    assert "ABCD: 32.0 ˚F  -99.0 ˚F  -99.00 %" in out
