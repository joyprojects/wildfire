import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import predict


def test_goes_threshold():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = runner.invoke(
            predict.goes_threshold,
            [
                "2019-10-27T20:00:00",
                "2019-10-27T20:01:00",
                "--satellite=noaa-goes17",
                "--region=M1",
                f"--goes_directory={temporary_directory}",
                f"--wildfire_directory={temporary_directory}",
                "--download",
            ],
        )
        assert actual.exit_code == 0
        assert (
            len(
                glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
            )
            > 0
        )
        assert len(glob.glob(os.path.join(temporary_directory, "*.json"))) == 1
