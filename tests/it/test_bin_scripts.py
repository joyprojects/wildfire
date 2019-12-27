import subprocess
import tempfile


def test_download_satellite_data():
    with tempfile.TemporaryDirectory() as temp_dir:
        actual = subprocess.run(
            [
                "download-satellite-data",
                "G17",
                "M1",
                "1",
                "2019-01-01T00:00:00",
                "2019-01-01T00:01:00",
                temp_dir,
            ],
        )
        assert actual.returncode == 0
