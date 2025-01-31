from setuptools import setup, find_packages
from pathlib import Path

# Read README.md with proper encoding
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="gocardless-fintools",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "nordigen-python",
        "click",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "gocardless-fintools=gocardless_connector.connector:cli",
        ],
    },
    author="thetombrider",
    author_email="tommasominuto@gmail.com",
    description="A CLI tool for managing bank account connections via GoCardless Bank Account Data API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thetombrider/gocardlessconnection",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
