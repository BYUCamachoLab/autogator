import setuptools
import re
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

verstr = "unknown"
try:
    verstrline = open('autogator/_version.py', "rt").read()
except EnvironmentError:
    # No version file.
    raise RuntimeError("Unable to find version in autogator/_version.py")
else:
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError("unable to find version in autogator/_version.py")

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
    version=verstr,
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
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'numpy',
        'matplotlib',
        'instrumental-lib',
        'opencv-python',
        'Pillow',
        'pywin32',
        'nicelib',
    ]
)