import setuptools
import re
import os

with open("README.md", "r") as fh:
    long_description = fh.read()


NAME = 'autogator'
LIBNAME = 'autogator'
from autogator import __version__, __website_url__  #analysis:ignore

extra_files = []
data_files_ext = []

def package_data_files(directory):
    paths =[]
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            name, ext = os.path.splitext(filename)
            if ext in data_files_ext:
                paths.append(os.path.join('..', path, filename))
    return paths

setuptools.setup(
    name="AutoGator",
    version=__version__,
    author="Sequoia Ploeg",
    author_email="sequoia.ploeg@ieee.org",
    description="A software package for camera-assisted motion control of PIC chip interrogation platforms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sequoiap/autogator",
    packages=setuptools.find_packages(),
    package_data={
        '': extra_files,
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        # 'numpy',
        # 'matplotlib',
        # 'instrumental-lib',
        # 'opencv-python',
        # 'Pillow',
        # 'pywin32',
        # 'nicelib',
    ]
)