import os
import subprocess
import sys

import autogator


def test_module_name():
    assert autogator.__name__ == "autogator"


def test_from_import_submodule():
    # Overriding __name__ in autogator/__init__.py made this raise
    # ModuleNotFoundError: No module named 'AutoGator'.
    from autogator import analysis

    assert analysis.__name__ == "autogator.analysis"


def test_data_dir_name():
    # Existing profiles and configuration live under this directory name.
    assert autogator.AUTOGATOR_DATA_DIR.name == "AutoGator"


def _run(code, tmp_path, **env):
    env = {**os.environ, "AUTOGATOR_LOGFILE": str(tmp_path / "test.log"), **env}
    result = subprocess.run(
        [sys.executable, "-c", code], env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return result


def test_logging_configures_package_logger(tmp_path):
    # autogator logging is set up at import time, so check it in a fresh
    # interpreter.
    _run(
        "import logging, autogator\n"
        "assert not logging.root.handlers\n"
        "log = logging.getLogger('autogator')\n"
        "assert log.level == logging.WARNING, log.level\n"
        "logging.getLogger('autogator.circuits').warning('logged to file')\n",
        tmp_path,
        AUTOGATOR_LOGLEVEL="warning",
    )
    assert "logged to file" in (tmp_path / "test.log").read_text()


def test_logging_respects_application_config(tmp_path):
    _run(
        "import logging\n"
        "logging.basicConfig()\n"
        "import autogator\n"
        "assert not logging.getLogger('autogator').handlers\n",
        tmp_path,
    )
    assert not (tmp_path / "test.log").exists()
