import pytest


class TestCircuit:
    def test_tostring(self):
        pass

    def test_getparameter(self):
        pass

    def test_set_new_parameter(self):
        pass

    def test_overwrite_parameter(self):
        pass

    def test_get_existing_parameter(self):
        pass

    def test_get_nonexistent_parameter(self):
        pass

    def test_copy(self):
        pass

    def test_deepcopy(self):
        pass


class TestLocation:
    def test_tostring(self):
        pass

    def test_add_location(self):
        pass

    def test_add_tuple(self):
        pass

    def test_add_incorrect_types(self):
        """
        Should fail. Tries ints, floats, strings, and lists.
        """
        pass

    def test_add_incorrect_types_tuple(self):
        """
        Should fail. Tries ints, floats, and strings.
        """
        pass

    def test_copy(self):
        pass

    def test_deepcopy(self):
        pass


class TestCircuitMap:
    def test_access_by_index(self):
        pass

    def test_access_by_location(self):
        pass

    def test_access_by_tuple(self):
        pass

    def test_add_maps(self):
        pass

    def test_tostring(self):
        pass

    def test_length(self):
        pass

    def test_copy(self):
        pass

    def test_deepcopy(self):
        pass

    def test_filterby(self):
        pass

    def test_filterout(self):
        pass

    def test_update_params(self):
        pass

    def test_savetxt(self):
        pass

    def test_loadtxt(self):
        pass

    def test_get_test_circuits(self):
        pass
