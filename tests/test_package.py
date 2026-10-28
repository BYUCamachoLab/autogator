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
