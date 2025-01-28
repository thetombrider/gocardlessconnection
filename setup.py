from setuptools import setup, find_packages

setup(
    name="bank-connector",
    version="0.2",
    packages=find_packages(),
    install_requires=[
        "python-dotenv",
        "nordigen-python",
        "click",
        "pandas"
    ],
    entry_points={
        "console_scripts": [
            "gocardless-connector=gocardless_connector.connector:cli",
        ],
    },
    author="thetombrider",
    author_email="tommasominuto@gmail.com",
    description="A CLI tool for managing bank account connections via GoCardless Bank Account Data API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/thetombrider/gocardlessconnection",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
