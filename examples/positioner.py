# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Positioner Example

This script allows you to save and goto positions on a stage. It assumes you
have the hardware configuration already set up, and loads the default
configuration.

To use this script, simply run:

```
python3 positioner.py
```

You will be presented with a prompt, and you can use the following command to
see a list of available commands:

```
>>> help
```

There are several potential use cases for this script. For example, if you
are performing chip leveling before lowering the fiber array, the best method
is by moving from edge to edge of the chip and determining height by comparing
the focus of a fixed microscope. By raising and lowering the microscope or the 
stage, you can progresively level the chip. In other words, once you can
move to all positions on the chip without having to adjust the distance of the
microscope, the plane of motion of your chip is level with respect to the
microscope. You could then lower a fixed fiber array near where the microscope
is looking and move the chip around its full travel without concern of crashing
into the fiber array.

Another use case is simply for easy navigation around the chip. Anytime you 
have fixed points you'll be returning to without doing things like scans or
sweeps in between (this would warrant a new script), this script will be
useful.
"""

from autogator.api import load_default_configuration
from autogator.hardware import Stage
from autogator.controllers import KeyboardControl, KeyloopKeyboardBindings, XboxBindings, XboxControl


def keyboard_control(stage: Stage):
    """
    Enters the default keyboard control loop with the default key bindings.

    Parameters
    ----------
    stage : Stage
        The stage configuration to use.
    """
    kc = KeyboardControl(stage, KeyloopKeyboardBindings())
    kc.loop()

def xbox_control(stage: Stage):
    """
    Enters the default xbox control loop with the default key bindings.

    Parameters
    ----------
    stage : Stage
        The stage configuration to use.
    """
    kc = XboxControl(stage, XboxBindings())
    kc.loop()


def print_help():
    cmds = {
        "COMMAND": "DESCRIPTION",
        "set <value>": "save current position as <value>",
        "goto <value>": "go to position <value>",
        "list": "list all saved positions",
        "ctrl": "enter keyboard control loop",
        "xbox": "enter xbox control loop",
        "help": "print this help message",
        "q": "quit this script",
    }
    width = max(len(name) for name in cmds)
    for cmd, desc in cmds.items():
        print(f"{cmd:<{width+2}} {desc}")


if __name__ == "__main__":
    scfg = load_default_configuration()
    stage = scfg.get_stage()

    positions = {}
    while True:
        cmd = input(">>> ")
        
        if cmd.startswith("set "):
            name = cmd[4:]
            positions[name] = stage.get_position()
            print("Saved position {} at {}".format(name, positions[name]))
        elif cmd.startswith("goto "):
            name = cmd[5:]
            stage.set_position(pos=positions[name])
        elif cmd == "list":
            print("Saved positions:")
            width = max(len(name) for name in positions)
            for name, position in positions.items():
                print(f"  {name:<{width+2}} {position}")
        elif cmd == "ctrl":
            keyboard_control(stage)
        elif cmd == "xbox":
            xbox_control(stage)
        elif cmd == "help":
            print_help()
        elif cmd == "q":
            break
