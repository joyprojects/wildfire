import os
import subprocess
import tempfile


def test_download_satellite_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = subprocess.run(
            [
                "download_satellite_data",
                "G17",
                "M1",
                "1",
                "2019-01-01T00:00:00",
                "2019-01-01T00:03:00",
                temp_dir,
            ],
            check=True,
        )
        assert actual.returncode == 0
        assert (
            len(
                os.listdir(
                    os.path.join(
                        temp_dir, "noaa-goes17", "ABI-L1b-RadM", "2019", "001", "00"
                    )
                )
            )
            == 3
        )


def test_download_satellite_data_bad_args():
    # directory does not already exists
    actual = subprocess.run(
        [
            "download_satellite_data",
            "G17",
            "M1",
            "1",
            "2019-01-01T00:00:00",
            "2019-01-01T00:01:00",
            "directory_does_not_exists",
        ],
    )
    assert actual.returncode == 2

    # bad satellite
    actual = subprocess.run(
        [
            "download_satellite_data",
            "bad-satellite",
            "M1",
            "1",
            "2019-01-01T00:00:00",
            "2019-01-01T00:01:00",
            "directory_does_not_exists",
        ],
    )
    assert actual.returncode == 2

    # bad region
    actual = subprocess.run(
        [
            "download_satellite_data",
            "G17",
            "bad-region",
            "1",
            "2019-01-01T00:00:00",
            "2019-01-01T00:01:00",
            "directory_does_not_exists",
        ],
    )
    assert actual.returncode == 2

    # bad channel
    actual = subprocess.run(
        [
            "download_satellite_data",
            "G17",
            "bad-region",
            "bad-channel",
            "2019-01-01T00:00:00",
            "2019-01-01T00:01:00",
            "directory_does_not_exists",
        ],
    )
    assert actual.returncode == 2
