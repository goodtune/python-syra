from setuptools import setup

version = "0.3"

setup(
    name="python-syra",
    version=version,
    url="http://www.touchtechnology.com.au/",
    author="Gary Reynolds",
    author_email="gary@touch.asn.au",
    description="Client for the Syra API.",
    install_requires=[
        "click",
        "first",
        "future",
        "python-dateutil",
        "suds-community",
        "ujson",
    ],
    packages=["syra"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={"console_scripts": ["syra = syra.cli:main"]},
)
