import autogator.data_cache as data_cache
import autogator.map as circuit_map


class ExperimentInterface:
    def __init__(self) -> None:
        self.cache = data_cache.DataCache.get_instance()
        self.laser = self.cache.get_laser()
        self.oscilliscope = self.cache.get_oscilliscope()
        self.circuits = self.cache.get_circuit_map().circuits

    def run(self):
        raise NotImplementedError

    def get_circuits(self) -> list[circuit_map.Circuit]:
        return self.circuits

    def set_circuits(self, circuits: list[circuit_map.Circuit]) -> None:
        self.circuits = circuits
