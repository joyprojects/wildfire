import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import predict


def test_goes_threshold(goes_level_2):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = runner.invoke(
            predict.goes_threshold,
            [
                "2019-10-27T20:01:00",
                "2019-10-27T20:02:00",
                "--satellite=noaa-goes17",
                "--region=C",
                f"--goes_directory={goes_level_2['level_1_directory']}",
                f"--persist_directory={temporary_directory}",
            ],
        )
        assert actual.exit_code == 0
        assert len(glob.glob(os.path.join(temporary_directory, "*.json"))) == 1
