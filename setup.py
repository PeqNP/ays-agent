#!/usr/bin/env python3
#
# Setup the ays-agent to be used as a stand-alone executable
#

from setuptools import setup, find_packages

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='ays_agent',
    version='0.9',
    authors = [
        {"name": "Eric Chamberlain", "email": "bitheadrl@protonmail.com"}
    ],
    description="@ys Agent Sensor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    readme="README.md",
    requires_python=">=3.8",
    install_requires=[
        "click>=7.1.2",
        "fastapi>=0.109.1",
        "fastapi-utils>=0.2.1",
        "psutil>=5.9.5",
        "PyYaml>=6.0",
        "requests>=2.31.0",
        "rich>=13.7.0",
        "typer>=0.9.0",
        "urllib3>=1.26.18,<2",
        "uvicorn>=0.18.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ays-agent = ays_agent.cli:app',
        ],
    },
)
