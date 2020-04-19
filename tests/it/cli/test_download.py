import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import download


def test_goes_level_1():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = runner.invoke(
            download.goes_level_1,
            [
                "2019-01-01T00:00:00",
                "2019-01-01T00:01:00",
                "--satellite=noaa-goes16",
                "--region=M2",
                f"--persist_directory={temporary_directory}",
            ],
        )
        assert actual.exit_code == 0
        assert (
            len(
                glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
            )
            == 16
        )


def test_goes_level_2():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = runner.invoke(
            download.goes_level_2,
            [
                "2020",
                "1",
                "1",
                "--satellite=noaa-goes16",
                "--product=ABI-L2-FDCC",
                f"--persist_directory={temporary_directory}",
            ],
        )
        assert actual.exit_code == 0
        assert (
            len(
                glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
            )
            == 288
        )
