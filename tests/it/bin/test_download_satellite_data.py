import os
import subprocess
import tempfile

import pytest


def test_run():
    with tempfile.TemporaryDirectory() as temporary_directory:
        subprocess.check_call(
            [
                "download_satellite_data",
                "noaa-goes17",
                "M1",
                "2019-01-01T00:00:00",
                "2019-01-01T00:01:00",
                temporary_directory,
            ],
        )
        assert (
            len(
                os.listdir(
                    os.path.join(temporary_directory, "ABI-L1b-RadM", "2019", "001", "00")
                )
            )
            == 16
        )


def test_bad_directory():
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.check_call(
            [
                "download_satellite_data",
                "noaa-goes17",
                "M1",
                "2019-01-01T00:00:00",
                "2019-01-01T00:01:00",
                "directory_does_not_exists",
            ],
        )


def test_bad_satellite():
    with tempfile.TemporaryDirectory() as temporary_directory:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call(
                [
                    "download_satellite_data",
                    "bad-satellite",
                    "M1",
                    "2019-01-01T00:00:00",
                    "2019-01-01T00:01:00",
                    temporary_directory,
                ],
            )


def test_bad_region():
    with tempfile.TemporaryDirectory() as temporary_directory:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_call(
                [
                    "download_satellite_data",
                    "noaa-goes17",
                    "bad-region",
                    "2019-01-01T00:00:00",
                    "2019-01-01T00:01:00",
                    temporary_directory,
                ],
            )
