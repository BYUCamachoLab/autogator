# User Guide

*AutoGator: The Automatic Chip Interrogator* is an open-source, cross-platform
code repository and framework with included hardware designs and
recommendations for assembling and controlling a photonic integrated circuit
(PIC) test station. It is designed to be used with
[PyroLab](https://pyrolab.readthedocs.io/en/latest/) but is extensible to
account for many other unique setups.

## Installation

### with pip <small>recommended</small> { data-toc-label="with pip" }

Stable versions are available through the Python Package Index (PyPI):

``` sh
pip install autogator
```

This will automatically install all required dependencies for you. Note that
AutoGator uses the modern build specification format, using ``pyproject.toml``
and ``setup.cfg`` files (see [PEP
517](https://www.python.org/dev/peps/pep-0517/), [PEP
518](https://www.python.org/dev/peps/pep-0518/)). Only later versions of
``pip`` and ``setuptools`` support this format, so you may need to upgrade them
first:

``` sh
pip install --upgrade pip setuptools
```

### with git

The source repository is available on GitHub:

``` sh
git clone https://github.com/BYUCamachoLab/autogator
```

It has dependencies on many other projects, which you should install yourself.
This can be done for you automatically by installing the repository in
"editable" mode:

``` sh
pip install -e autogator
```
