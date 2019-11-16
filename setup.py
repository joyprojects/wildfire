"""Packaging for the GOES library."""
from setuptools import find_packages, setup


def get_version():
    """Get library version."""
    with open("VERSION") as buff:
        return buff.read()


setup(
    name="goes",
    version=get_version(),
    url="https://github.com/Ferrumofomega/goes",
    author="",
    author_email="",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.in").readlines(),
    tests_require=open("requirements-dev.in").readlines(),
    description="Utilities for working with GOES 16/17 satellite data",
    long_description="\n" + open("README.md").read(),
)
