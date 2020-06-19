"""
Convert the channel data in a tdms file
to a 4-byte float file
"""

from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent

# Get the long description from the README file
readme=here / 'README.md'
with open(readme, encoding='utf-8') as f:
    long_description = f.read()

PROJECT_NAME="tdms2bin"
exec(open(here / "tdms2bin/version.py").read())

VERSION=__version__
DESCRIPTION="Convert channel data in a tdms file to f4"
URL="https://github.com/flyrok/fft_tdms"
AUTHOR="A Ferris"
EMAIL="aferris@ara.com"
CLASSIFIERS=['Development Status :: 3 - Alpha',
    'Intended Audience :: Scientists ',
    'Topic :: TDMS:: Helper Scripts',
    'License :: OSI Approved :: GPL-3 License',
     'Programming Language :: Python :: 3']
KEYWORDS="tdms"     

INSTALL_REQUIRES = [
    'numpy>=1.6.1',
    'nptdms',
    'configparser',
    ]

setup(
    name=PROJECT_NAME,  # Required
    version=VERSION,  # Required
    description=DESCRIPTION,  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url=URL,  # Optional
    author=AUTHOR,  # Optional
    author_email=EMAIL,  # Optional
    classifiers=CLASSIFIERS ,
    keywords=KEYWORDS,  # Optional
    python_requires='>=3.6',
    include_package_data=True,
    packages=['tdms2bin'],
    entry_points={  # Optional
        'console_scripts': [
            'tdms2bin=tdms2bin.tdms2bin:main',
        ],
    },
    install_requires=INSTALL_REQUIRES,
    extras_require={},
    package_data={  
    },
    project_urls={  # Optional
        'Source': URL,
    },
)

