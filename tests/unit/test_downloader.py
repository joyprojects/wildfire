import os
import tempfile

from wildfire.goes import downloader


def test_make_necessary_directories():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "this/is/a/test/filepath/")
        assert not os.path.exists(file_path)
        downloader.make_necessary_directories(file_path)
        assert os.path.exists(file_path)
