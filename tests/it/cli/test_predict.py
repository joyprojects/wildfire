import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import predict


def test_goes_threshold():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        goes_directory = os.path.join("tests", "resources", "goes_level_1_scan_wildfire")
        actual = runner.invoke(
            predict.goes_threshold,
            [
                "2019-10-27T20:00:00",
                "2019-10-27T20:01:00",
                "--satellite=noaa-goes17",
                "--region=M1",
                f"--goes_directory={goes_directory}",
                f"--wildfire_directory={temporary_directory}",
            ],
        )
        assert actual.exit_code == 0
        assert len(glob.glob(os.path.join(temporary_directory, "*.json"))) == 1
