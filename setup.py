import pathlib
from setuptools import setup, find_packages

import crypto_factory as cf

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README.md file
README = (HERE / "README.md").read_text()

# Requirements list
REQUIRED_PKGS = (HERE / "requirements.txt").read_text().split()

# This call to setup() does all the work
setup(
    name=cf.__title__,
    version=cf.__version__,
    author=cf.__author__,
    author_email=cf.__email__,
    description=cf.__summary__,
    long_description=README,
    long_description_content_type="text/markdown",
    # long_description_content_type="text/x-rst",
    url=cf.__uri__,
    license=cf.__license__,
    packages=find_packages(exclude=("tests", "private", )),
    include_package_data=True,
    platforms='any',
    # zip_safe=False,
    python_requires='>=3.4',
    install_requires=REQUIRED_PKGS,
    test_suite="tests",
    keywords='cryptography factory-design',
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Security :: Cryptography",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    project_urls={
        'Documentation': 'https://' + cf.__title__.lower() + '.readthedocs.io/en/latest/',
        'Releases': 'https://pypi.org/project/' + cf.__title__,
        'Source': cf.__uri__,
        'Tracker': cf.__uri__ + '/issues',
    },
)
