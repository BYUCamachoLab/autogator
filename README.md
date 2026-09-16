<p align="center">
<img src="https://raw.githubusercontent.com/BYUCamachoLab/autogator/master/docs/images/autogator.png" width="40%" alt="PyroLab">
</p>

<p align="center">
<a href="https://github.com/BYUCamachoLab/autogator/tags"><img alt="Development version" src="https://img.shields.io/github/v/tag/BYUCamachoLab/autogator?label=master&color=informational"></a>
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
editable mode:

```
pip install -e .
```

For development, [uv](https://docs.astral.sh/uv/) will create a virtual
environment and install the project along with the development and
documentation dependency groups, all pinned by ``uv.lock``:

```
uv sync
```

Useful commands from there:

```
uv run pytest             # run the test suite
uv run isort .            # sort imports
uv run zensical serve     # preview the documentation at localhost:8000
```

To build only the documentation, without the package or its runtime
dependencies:

```
uv sync --only-group docs
uv run --no-project zensical build
```

Note that the whole API reference under ``docs/api`` is generated from the
docstrings in ``autogator/`` by mkdocstrings, and Zensical's build cache keys on
the Markdown files rather than on those Python sources. After editing a
docstring, pass ``--clean`` to rebuild the API pages:

```
uv run zensical build --clean
```

Read the Docs builds from a fresh checkout every time, so this only affects
local builds. Also note that classes and functions without a docstring are
omitted from the reference entirely.

## Uninstallation

PyroLab creates data and configuration directories that aren't deleted when pip
uninstalled. You can find their locations by running (before uninstallation):

```
import autogator
print(autogator.AUTOGATOR_DATA_DIR)
```

This folder can be safely deleted after uninstallation.

## Releasing

Make sure you have committed a changelog file under ``docs/changelog`` titled 
``<major>.<minor>.<patch>-changelog.md`` before bumping version. Also, the git
directory should be clean (no uncommitted changes).

The version is declared in exactly one place, the ``version`` field of
``pyproject.toml``. ``autogator.__version__`` reads it back from the installed
distribution metadata, so there is nothing else to keep in sync.

To bump version prior to a release, run one of the following commands:

```
uv version --bump major
uv version --bump minor
uv version --bump patch
```

Unlike bumpversion, which this project used previously, ``uv version`` only
edits ``pyproject.toml`` (and refreshes ``uv.lock``); it does not commit or tag.
Commit the change and tag it yourself:

```
git commit -am "Bump version to $(uv version --short)"
git tag "v$(uv version --short)"
```

Releases are automatically published to PyPI and GitHub when git tags matching
the "v*" pattern are pushed (e.g. "v0.2.1"), so push the tag to trigger the
release workflow:

```
git push origin master --follow-tags
```

For code quality, please run isort and black before committing (note that the
latest release of isort may not work through VSCode's integrated terminal, and
it's safest to run it separately through another terminal).
