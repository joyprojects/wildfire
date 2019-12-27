"""Packaging for the GOES library."""
from setuptools import find_packages, setup


def get_version():
    """Get library version."""
    with open("VERSION") as buff:
        return buff.read()


setup(
    name="wildfire",
    version=get_version(),
    url="https://github.com/Ferrumofomega/goes",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.in").readlines(),
    tests_require=open("requirements-dev.in").readlines(),
    description="Modelling characteristics of wildfires",
    long_description="\n" + open("README.md").read(),
    scripts=["bin/download_satellite_data"],
)
