from setuptools import setup

__version_info__ = ('0', '3', '2')
__version__ = '.'.join(__version_info__)

setup(
    name="staticjinja",
    version=__version__,
    description="jinja based static site generator",
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    url="https://github.com/Ceasar/staticjinja",
    keywords=["jinja", "static", "website"],
    packages=["staticjinja"],
    entry_points={
        'console_scripts': [
            'staticjinja = staticjinja.cli:main',
        ],
    },
    install_requires=[
        "docopt",
        "easywatch",
        "jinja2",
    ],
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    ]
)
