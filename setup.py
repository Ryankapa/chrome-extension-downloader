#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for Chrome Extension Downloader
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="chrome-extension-downloader",
    version="2.0.0",
    author="Chrome Extension Downloader Team",
    author_email="",
    description="Enhanced tool for downloading Chrome extensions from the Chrome Web Store",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/chrome-extension-downloader",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Packaging",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "yaml": [
            "pyyaml>=6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "chrome-extension-downloader=chrome_extension_downloader:main",
            "ced=chrome_extension_downloader:main",
        ],
    },
    keywords="chrome extension downloader crx zip webstore automation",
    project_urls={
        "Bug Reports": "https://github.com/your-username/chrome-extension-downloader/issues",
        "Source": "https://github.com/your-username/chrome-extension-downloader",
        "Documentation": "https://github.com/your-username/chrome-extension-downloader#readme",
    },
    include_package_data=True,
    zip_safe=False,
)
