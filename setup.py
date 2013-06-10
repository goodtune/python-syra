from distutils.core import setup
from string import strip

version = "0.2"

setup(
    name = 'python-syra',
    version = version,
    url = 'http://www.touchtechnology.com.au/',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = 'Client for the Syra API.',
    install_requires = filter(None, map(strip, open('requirements.txt'))),
    packages = ['syra'],
)
