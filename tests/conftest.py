import glob
import os

import pytest
import xarray as xr

from wildfire.data import goes_level_1


@pytest.fixture()
def l1_reflective_band():
    return xr.load_dataset(
        os.path.join(
            "tests",
            "resources",
            "goes_level_1_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "OR_ABI-L1b-RadM1-M6C01_G17_s20193002000275_e20193002000332_c20193002000379.nc",
        )
    )


@pytest.fixture()
def l1_emissive_band():
    return xr.load_dataset(
        os.path.join(
            "tests",
            "resources",
            "goes_level_1_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "OR_ABI-L1b-RadM1-M6C07_G17_s20193002000275_e20193002000344_c20193002000390.nc",
        )
    )


@pytest.fixture()
def l1_all_bands_wildfire():
    return [
        goes_level_1.read_netcdf(local_filepath=filepath)
        for filepath in glob.glob(
            os.path.join(
                "tests",
                "resources",
                "goes_level_1_scan_wildfire",
                "ABI-L1b-RadM",
                "2019",
                "300",
                "20",
                "*.nc",
            )
        )
    ]


@pytest.fixture()
def l1_all_bands_no_wildfire():
    return [
        goes_level_1.read_netcdf(local_filepath=filepath)
        for filepath in glob.glob(
            os.path.join(
                "tests",
                "resources",
                "goes_level_1_scan_no_wildfire",
                "ABI-L1b-RadM",
                "2019",
                "335",
                "10",
                "*.nc",
            )
        )
    ]


@pytest.fixture()
def l1_wildfire_scan_filepaths():
    return glob.glob(
        os.path.join(
            "tests",
            "resources",
            "goes_level_1_scan_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "300",
            "20",
            "*.nc",
        )
    )


@pytest.fixture()
def l1_no_wildfire_scan_filepaths():
    return glob.glob(
        os.path.join(
            "tests",
            "resources",
            "goes_level_1_scan_no_wildfire",
            "ABI-L1b-RadM",
            "2019",
            "335",
            "10",
            "*.nc",
        )
    )


@pytest.fixture()
def s3_l1_filepath():
    return (  # in the format used by the s3fs library
        "noaa-goes17/ABI-L1b-RadM/2019/001/00/"
        "OR_ABI-L1b-RadM1-M3C01_G17_s20190010000270_e20190010000327_c20190010000358.nc"
    )


@pytest.fixture()
def l2_wildfire():
    l1_directory = os.path.join(
        "tests", "resources", "goes_level_2_band", "matching_level_1_scan"
    )
    return {
        "l2": xr.load_dataset(
            os.path.join(
                "tests",
                "resources",
                "goes_level_2_band",
                "level_2_scan",
                "OR_ABI-L2-FDCC-M6_G16_s20200040316182_e20200040318554_c20200040319252.nc",
            )
        ),
        "l1": goes_level_1.read_netcdfs(
            glob.glob(os.path.join(l1_directory, "**", "*.nc",), recursive=True)
        ),
        "l1_directory": l1_directory,
    }
