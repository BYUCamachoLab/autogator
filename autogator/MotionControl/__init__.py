import os
from enum import Enum

# Add location of the DLLs to PATH so that the program can run on any machine
dll_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dll')
os.environ['PATH'] = dll_location + os.pathsep + os.environ['PATH']

class CINT(Enum):
    """
    An enumeration of basic c-style integer constants.
    """
    CHAR_MIN = -128
    CHAR_MAX = 127
    SHRT_MIN = -32768
    SHRT_MAX = 32767
    USHRT_MAX = 65535
    INT_MIN = -2147483648
    INT_MAX = 2147483647
    UINT_MAX = 4294967295 

class list1(object):
    """
    A list that is 1-indexed, not 0- indexed.
    """
    def __init__(self, vals: list=None):
        self.list = [] if vals is None else vals

    def __getitem__(self, index):
        return self.list[index - 1]

    def __setitem__(self, index, value):
        self.list[index - 1] = value