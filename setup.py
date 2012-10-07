from distutils.core import setup

from staticjinja import __version__


setup(
    name="staticjinja",
    version=__version__,
    description="jinja based static site generator",
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    url="https://github.com/Ceasar/staticjinja",
    packages=["staticjinja"]
)
