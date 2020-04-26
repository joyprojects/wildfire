import glob
import os

import pytest
import xarray as xr

RESOURCES_DIR = os.path.join("tests", "resources")


@pytest.fixture()
def goes_level_1_mesoscale():
    return xr.load_dataset(
        os.path.join(
            RESOURCES_DIR,
            "OR_ABI-L1b-RadM1-M6C01_G16_s20200010001262_e20200010001320_c20200010001364.nc",
        )
    )


@pytest.fixture()
def goes_level_1_conus():
    return xr.load_dataset(
        os.path.join(
            RESOURCES_DIR,
            "OR_ABI-L1b-RadC-M6C01_G17_s20193002001196_e20193002003569_c20193002004019.nc",
        )
    )


@pytest.fixture()
def goes_level_1_full():
    return xr.load_dataset(
        os.path.join(
            RESOURCES_DIR,
            "OR_ABI-L1b-RadF-M6C03_G16_s20193000000373_e20193000010081_c20193000010142.nc",
        )
    )


@pytest.fixture()
def goes_level_1_channel_1():
    return xr.load_dataset(
        os.path.join(
            RESOURCES_DIR,
            "goes_level_1_scan_no_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "335",
            "10",
            "OR_ABI-L1b-RadM1-M6C01_G17_s20193351027275_e20193351027332_c20193351027383.nc",
        )
    )


@pytest.fixture()
def goes_level_1_channel_7():
    return xr.load_dataset(
        os.path.join(
            RESOURCES_DIR,
            "goes_level_1_scan_no_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "335",
            "10",
            "OR_ABI-L1b-RadM1-M6C07_G17_s20193351027275_e20193351027344_c20193351027394.nc",
        )
    )


@pytest.fixture()
def goes_level_1_filepaths_wildfire():
    return glob.glob(
        os.path.join(
            RESOURCES_DIR, "goes_level_2", "matching_level_1_scan", "**", "*.nc",
        ),
        recursive=True,
    )


@pytest.fixture()
def goes_level_1_filepaths_no_wildfire():
    return glob.glob(
        os.path.join(RESOURCES_DIR, "goes_level_1_scan_no_wildfire", "**", "*.nc",),
        recursive=True,
    )


@pytest.fixture()
def s3_goes_level_1_filepath():
    return (  # in the format used by the s3fs library
        "noaa-goes17/ABI-L1b-RadM/2019/001/00/"
        "OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    )


@pytest.fixture()
def goes_level_2():
    level_1_directory = os.path.join(
        RESOURCES_DIR, "goes_level_2", "matching_level_1_scan"
    )
    return {
        "level_2": os.path.join(
            RESOURCES_DIR,
            "goes_level_2",
            "band",
            "OR_ABI-L2-FDCC-M6_G17_s20193002001196_e20193002003569_c20193002004132.nc",
        ),
        "level_1": glob.glob(
            os.path.join(level_1_directory, "**", "*.nc",), recursive=True
        ),
        "level_1_directory": level_1_directory,
    }
