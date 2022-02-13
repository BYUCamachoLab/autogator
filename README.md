<p align="center">
<img src="https://raw.githubusercontent.com/BYUCamachoLab/autogator/master/docs/images/autogator.png" width="40%" alt="PyroLab">
</p>

<p align="center">
<img alt="Development version" src="https://img.shields.io/badge/master-v0.3.0-informational">
<a href="https://pypi.python.org/pypi/autogator"><img alt="PyPI Version" src="https://img.shields.io/pypi/v/autogator.svg"></a>
<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/autogator">
<a href="https://autogator.readthedocs.io/"><img alt="Documentation Status" src="https://readthedocs.org/projects/autogator/badge/?version=latest"></a>
<a href="https://pypi.python.org/pypi/autogator/"><img alt="License" src="https://img.shields.io/pypi/l/autogator.svg"></a>
<a href="https://github.com/BYUCamachoLab/autogator/commits/master"><img alt="Latest Commit" src="https://img.shields.io/github/last-commit/BYUCamachoLab/autogator.svg"></a>
</p>

# AutoGator 

AutoGator: The Automatic Chip Interrogator

A software package for camera-assisted motion control and experiment 
configuration of photonic integrated circuit interrogation platforms.

Developed by Sequoia Ploeg (for [CamachoLab](https://camacholab.byu.edu/) at
Brigham Young University).

## Installation

AutoGator is a client with algorithms for interacting with instruments 
controlled by other softwares. It typically communicates with hardware using
socket connections.

This package is cross-platform and can be installed on any operating system.

AutoGator can be installed using pip:

```
pip install autogator
```

You can also clone the repository, navigate to the toplevel, and install in
editable mode (make sure you have pip >= 21.1):

pip install -e .

## Uninstallation

PyroLab creates data and configuration directories that aren't deleted when pip
uninstalled. You can find their locations by running (before uninstallation):

```
import autogator
print(autogator.AUTOGATOR_DATA_DIR)
```

This folder can be safely deleted after uninstallation.

## For Developers

To bump version prior to a release, run one of the following commands:

```
bumpversion major
bumpversion minor
bumpversion patch
```

For code quality, please run isort and black before committing (note that the
latest release of isort may not work through VSCode's integrated terminal, and
it's safest to run it separately through another terminal).

Releases are automatically created when git tags matching the "v*" pattern are
created.
