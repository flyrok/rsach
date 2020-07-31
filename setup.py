"""
Cmdline program to read specific sac header values

"""

from setuptools import setup, find_packages
from pathlib import Path

here = Path(__file__).resolve().parent

# Get the long description from the README file
readme=here / 'README.md'
with open(readme, encoding='utf-8') as f:
    long_description = f.read()

PROJECT_NAME="rsach"
exec(open(here / "rsach/version.py").read())

VERSION=__version__
DESCRIPTION="Convert channel data in a tdms file to f4"
URL="https://github.com/flyrok/rsach"
AUTHOR="A Ferris"
EMAIL="flyrok@gmail.com"
CLASSIFIERS=['Development Status :: 3 - Alpha',
    'Intended Audience :: Scientists ',
    'Topic :: TDMS:: Helper Scripts',
    'License :: OSI Approved :: GPL-3 License',
     'Programming Language :: Python :: 3']
KEYWORDS="sac header"     

INSTALL_REQUIRES = [
    'obspy',
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
    packages=['rsach'],
    entry_points={  # Optional
        'console_scripts': [
            'rsach=rsach.rsach:main',
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

