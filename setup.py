"""Packaging."""
from setuptools import find_packages, setup


def get_version():
    """Get library version."""
    with open("VERSION") as buff:
        return buff.read()


setup(
    name="wildfire",
    version=get_version(),
    url="https://github.com/joyprojects/wildfire",
    author="Joy Projects",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    description="Modelling characteristics of wildfires",
    long_description="\n" + open("README.md").read(),
    entry_points={
        "console_scripts": [
            "predict=wildfire.cli.predict:predict",
            "download=wildfire.cli.download:download",
            "training-data=wildfire.cli.training_data:training_data",
        ]
    },
)
