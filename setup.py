from setuptools import find_packages, setup

setup(
    name="caching_proxy_server",
    version="1.0.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["caching-proxy=src.cli:app"]},
)
