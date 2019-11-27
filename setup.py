from setuptools import setup

setup(
    name="python-syra",
    url="http://www.touchtechnology.com.au/",
    author="Gary Reynolds",
    author_email="gary@touch.asn.au",
    description="Client for the Syra API.",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
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
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={"console_scripts": ["syra = syra.cli:main"]},
)
