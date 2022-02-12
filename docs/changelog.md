# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- insertion marker -->
## [0.3.0](https://github.com/BYUCamachoLab/autogator/releases/tag/0.3.0) - 2022-02-07

### Added
- First public release.
- Support for multiple configuration profiles, allows you to create multiple
  hardware configurations or setups to load into the program.

### Changed
- Only supports Python 3.7+.
- Moved to ``pyproject.toml`` and ``setup.cfg`` files.
- Default data directory is no longer a system-managed folder (caused headaches
  on Linux)
- Switched to GPLv3+ license to protect open-source nature of this work.

### Removed
- Support for Python versions 3.6 and below removed.