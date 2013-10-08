import os
from setuptools import setup, find_packages

dependencies = ['Flask', 'pyquery', 'requests', 'BeautifulSoup']

setup(
    name = "schmoxy",
    version = "0.01",
    author = "Ulas Tuerkmen",
    author_email = "ulas.tuerkmen@gmail.com",
    description = ("A proxy for mirroring other web pages with minor replacements"),
    install_requires = dependencies,
    packages=find_packages(),
    zip_safe=False,
    entry_points = {'console_scripts': ['runit = schmoxy:runit']}
)
