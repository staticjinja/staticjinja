from setuptools import setup
from os import path

cwd = path.abspath(path.dirname(__file__))

# Read in version info
with open(path.join(cwd, 'staticjinja', 'version.py')) as f:
    versions = {}
    exec(f.read(), versions)

# Read the contents of our README file
with open(path.join(cwd, 'README.rst')) as f:
    long_description = f.read()

setup(
    name="staticjinja",
    version=versions["__version__"],
    description="jinja based static site generator",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author="Ceasar Bautista",
    author_email="cbautista2010@gmail.com",
    maintainer="Nick Crews",
    maintainer_email="nicholas.b.crews@gmail.com",
    url="https://github.com/staticjinja/staticjinja",
    project_urls={
        "Documentation": "https://staticjinja.readthedocs.io",
        "GitHub Project": "https://github.com/staticjinja/staticjinja",
        "Issue Tracker": "https://github.com/staticjinja/staticjinja/issues"
    },
    python_requires=">=3.6",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
    ]
)
