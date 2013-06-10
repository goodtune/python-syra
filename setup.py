from distutils.core import setup
from string import strip

version = "0.3"

setup(
    name = 'python-syra',
    version = version,
    url = 'http://www.touchtechnology.com.au/',
    author = 'Gary Reynolds',
    author_email = 'gary@touch.asn.au',
    description = 'Client for the Syra API.',
    install_requires = filter(None, map(strip, open('requirements.txt'))),
    packages = ['syra'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python',
        'Topic :: Internet :: Name Service (DNS)',
        'Topic :: Software Development :: Libraries :: Python Modules',
   ],
)
