from setuptools import setup, find_packages
import os

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join("nfc_library", "__init__.py"), encoding="utf-8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break
    else:
        version = "0.1.0" 

setup(
    name="nfc-library",
    version=version,
    author="Ahmed Abdelkhalek",
    author_email="opensource@mgtk.io",
    description="A high-level Python wrapper library for NFC operations",
    url="https://github.com/ahmed93/python-nfclib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    project_urls={
        "Bug Tracker": "https://github.com/ahmed93/python-nfclib/issues",
        "Documentation": "https://github.com/ahmed93/python-nfclib#readme",
        "Source Code": "https://github.com/ahmed93/python-nfclib",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    keywords="nfc, rfid, acr122u, ndef",
    packages=find_packages(include=["nfc_library", "nfc_library.*"]),
    python_requires=">=3.9",
    install_requires=[
        "nfcpy",
        "ndef",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "isort", "mypy"],
        "docs": ["sphinx", "sphinx_rtd_theme"],
    },
    entry_points={
        "console_scripts": [
            "nfc-interactive=nfc_library.cli:main",
        ],
    },
)