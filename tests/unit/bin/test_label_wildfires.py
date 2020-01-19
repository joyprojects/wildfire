import json
import os
import subprocess
import tempfile


def test_run():
    with tempfile.TemporaryDirectory() as temporary_directory:
        subprocess.check_call(
            [
                "label_wildfires",
                "noaa-goes17",
                "M1",
                "2019-10-27T20:00:00",
                "2019-10-27T20:01:00",
                os.path.join("tests", "resources", "test_scan_wildfire"),
                temporary_directory,
            ],
        )
        assert len(os.listdir(temporary_directory)) == 1
