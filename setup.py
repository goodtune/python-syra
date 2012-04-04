from distutils.core import setup

version = "0.1.2"

setup(
    name = 'python-syra',
    version = version,
    url = 'http://www.touchtechnology.com.au/',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = 'Client for the Syra API.',
    install_requires = ['suds', 'python-dateutil<2.0'],
    packages = ['syra'],
)
