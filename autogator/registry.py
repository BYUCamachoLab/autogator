from autogator import __CONFIG_DIR__

import yaml

import os.path
from os import path

global registry

def get_registry():
    global registery
    if registry is null:
        registry = Registry()
    return registery

class Registry:
    def __init__(self):
        if path.exists("config.yml"):
            stream = open("config.yml", 'r')
            self.register = yaml.load(stream)
            stream.close()
        else: 
            self.register = {}
​
    def register(self, name, device, parameters):
        self.register[name] = device
​
    def get(self, name):
        # importlib.import_module('.c', __name__)
        return device
​
    def save(self):
        stream = open("config.yml", 'w')
        yaml.dump(self.register)

​
class LocalDevice:
    pass
​
class PyrolabDevice:
    pass
​
