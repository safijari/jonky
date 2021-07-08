from setuptools import setup, find_packages
import os

setup(
    name="jonky",
    version="0.0.1",
    description="jonky, Jari's conky",
    author="Jariullah Safi",
    author_email="safijari@isu.edu",
    packages=find_packages(),
    install_requires=[
        "pycairo",
        "PyGObject",
        "pillow",
        "maya",
        "libjari",
        "bash",
        "orgparse",
        "psutil",
        "numpy"
    ],
)
