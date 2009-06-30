import sys
from setuptools import setup, find_packages
from chameleon import __version__

setup(
    name='chameleon',
    version=__version__,
    description="A schema transformation tool.",
    author="Jeff Ortel",
    author_email="jortel@redhat.com",
    maintainer="Jeff Ortel",
    maintainer_email="jortel@redhat.com",
    packages=find_packages(),
)
