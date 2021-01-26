from __future__ import annotations

from typing import NamedTuple


# In these named tuples, __str__ is for informal representation, like text
# output, while __repr__ is for object representation within an interpreter.

class ChipFile:
    '''
    circuits is a dict of locations to circuit descriptions.
    '''
    def __init__(self, filename):
        self.filename = filename
        self.devices = []

class Location(NamedTuple):
    x: int
    y: int

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

class DeviceEntry(NamedTuple):
    loc: Location
    device_id: str
    name: str
    ports: str = "LDDND"
    mode: str = "TE"
    submitter: str = "root"

    def __str__(self) -> str:
        return f"{self.loc} " \
            f"{self.device_id} " \
            f"name={self.name} " \
            f"ports={self.ports} " \
            f"mode={self.mode} " \
            f"submitter='{self.submitter}'"

class DeviceList(list):
    def __str__(self) -> str:
        out = ""
        for device in self:
            out += str(device) + "\n"
        return out


if __name__ == "__main__":
    d = DeviceList()
    d.append(DeviceEntry(Location(3, 4), "sequoiap_mzi_0_jog40_0", "sequoia_mzi", "LNND", "TE", "sequoiac"))
    d.append(DeviceEntry(Location(3, 14), "sequoiap_mzi_0_jog40_1", "sequoia_mzi", "LNND", "TE", "sequoiac"))
    d.append(DeviceEntry(Location(3, 24), "sequoiap_mzi_0_jog40_2", "sequoia_mzi", "LNND", "TE", "sequoiac"))
    d.append(DeviceEntry(Location(3, 34), "sequoiap_mzi_2_jog40_0", "sequoia_mzi2", "LNND", "TE", "sequoiac"))
    d.append(DeviceEntry(Location(3, 44), "sequoiap_mzi_2_jog40_1", "sequoia_mzi2", "LNND", "TE", "sequoiac"))

    print(d)
