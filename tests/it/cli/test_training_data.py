import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import training_data


def test_goes_l2_cnn():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        actual = runner.invoke(
            training_data.goes_l2_cnn,
            [
                os.path.join(
                    "tests", "resources", "goes_level_2_band", "matching_level_1_scan"
                ),
                os.path.join("tests", "resources", "goes_level_2_band", "level_2_scan"),
                f"--persist_directory={temporary_directory}",
                "--height=32",
                "--width=32",
                "--stride=32",
            ],
        )
        assert actual.exit_code == 0
        assert (
            len(
                glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
            )
            == 1
        )
