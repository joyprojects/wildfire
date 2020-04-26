import glob
import os
import tempfile

from click.testing import CliRunner

from wildfire.cli import training_data


def test_goes_l2_cnn(goes_level_2):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as temporary_directory:
        level_2_directory = os.path.dirname(goes_level_2["level_2"])
        actual = runner.invoke(
            training_data.goes_l2_cnn,
            [
                goes_level_2["level_1_directory"],
                level_2_directory,
                f"--persist_directory={temporary_directory}",
                "--height=32",
                "--width=32",
                "--stride=32",
            ],
        )
        assert actual.exit_code == 0
        assert len(
            glob.glob(os.path.join(temporary_directory, "**", "*.nc"), recursive=True)
        ) == len(glob.glob(os.path.join(level_2_directory, "**", "*.nc"), recursive=True))
