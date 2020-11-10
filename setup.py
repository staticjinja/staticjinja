from setuptools import setup

# Read in version info
with open('staticjinja/version.py') as f:
    versions = {}
    exec(f.read(), versions)

setup(
    name="staticjinja",
    version=versions["__version__"],
    description="jinja based static site generator",
    author="Ceasar Bautista, Nick Crews",
    author_email="cbautista2010@gmail.com, nicholas.b.crews@gmail.com",
    url="https://github.com/staticjinja/staticjinja",
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
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
    ]
)
