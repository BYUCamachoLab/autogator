# -*- coding: utf-8 -*-
#
# Copyright © Autogator Project Contributors
# Licensed under the terms of the GNU GPLv3+ License
# (see autogator/__init__.py for details)

"""
# Controllers

AutoGator can be commanded by a variety of different controllers. The default
is a keyboard controller, but you can also use a joystick or a mouse, or even
an XBox controller. More controllers may be implmemented here in the future.
"""

import logging
import threading
import time

import keyboard
from pydantic import BaseModel, BaseSettings

from autogator.hardware import Stage


log = logging.getLogger(__name__)


class KeyloopKeyboardBindings(BaseSettings):
    """
    Sets default keyboard bindings for the KeyboardControl controller.

    Because settings are implemented using Pydantic, environmental variables
    can be used to override the default settings.
    """
    MOVE_LEFT: str = "left arrow"
    MOVE_RIGHT: str = "right arrow"
    MOVE_UP: str = "up arrow"
    MOVE_DOWN: str = "down arrow"
    MOVE_RAISE: str = "="
    MOVE_LOWER: str = "-"
    JOG_LEFT: str = "a"
    JOG_RIGHT: str = "d"
    JOG_UP: str = "w"
    JOG_DOWN: str = "s"
    JOG_CLOCKWISE: str = "c"
    JOG_COUNTERCLOCKWISE: str = "x"
    LINEAR_JOG_STEP: str = "shift + j"
    ROTATIONAL_JOG_STEP: str = "shift + g"
    STOP_ALL: str = "space"
    HOME: str = "o"
    HELP: str = "h"
    QUIT: str = "q"


class KeyboardControl:
    """
    Implmements functions for the keyboard controller.

    Debounces key presses to make sure that the stage does not get placed 
    into a deadlocked or unrecoverable state.
    """
    def __init__(self, stage: Stage, bindings: KeyloopKeyboardBindings = None):
        self.stage = stage

        if bindings is None:
            bindings = KeyloopKeyboardBindings()
        self.bindings = bindings

        self.semaphores = {
            "MOTOR_X" : threading.Semaphore(),
            "MOTOR_Y" : threading.Semaphore(),
            "MOTOR_Z" : threading.Semaphore(),
            "MOTOR_PSI" : threading.Semaphore(),
        }

        self.linear_step_size = 0.1
        self.rotational_step_size = 0.1

    def _move_left(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_cont("backward")
            while keyboard.is_pressed(self.bindings.MOVE_LEFT):
                time.sleep(0.05)
            self.stage.x.stop()
            semaphore.release()

    def _move_right(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_cont("forward")
            while keyboard.is_pressed(self.bindings.MOVE_RIGHT):
                time.sleep(0.05)
            self.stage.x.stop()
            semaphore.release()

    def _move_up(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_cont("forward")
            while keyboard.is_pressed(self.bindings.MOVE_UP):
                time.sleep(0.05)
            self.stage.y.stop()
            semaphore.release()

    def _move_down(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_cont("backward")
            while keyboard.is_pressed(self.bindings.MOVE_DOWN):
                time.sleep(0.05)
            self.stage.y.stop()
            semaphore.release()

    def _move_raise(self):
        semaphore = self.semaphores["MOTOR_Z"]
        if semaphore.acquire(timeout=0.1):
            self.stage.z.move_cont("forward")
            while keyboard.is_pressed(self.bindings.MOVE_RAISE):
                time.sleep(0.05)
            self.stage.z.stop()
            semaphore.release()

    def _move_lower(self):
        semaphore = self.semaphores["MOTOR_Z"]
        if semaphore.acquire(timeout=0.1):
            self.stage.z.move_cont("backward")
            while keyboard.is_pressed(self.bindings.MOVE_LOWER):
                time.sleep(0.05)
            self.stage.z.stop()
            semaphore.release()

    def _jog_left(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_by(-self.linear_step_size)
            semaphore.release()

    def _jog_right(self):
        semaphore = self.semaphores["MOTOR_X"]
        if semaphore.acquire(timeout=0.1):
            self.stage.x.move_by(self.linear_step_size)
            semaphore.release()

    def _jog_up(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_by(self.linear_step_size)
            semaphore.release()

    def _jog_down(self):
        semaphore = self.semaphores["MOTOR_Y"]
        if semaphore.acquire(timeout=0.1):
            self.stage.y.move_by(-self.linear_step_size)
            semaphore.release()

    def _jog_cw(self):
        semaphore = self.semaphores["MOTOR_PSI"]
        if semaphore.acquire(timeout=0.1):
            self.stage.psi.move_by(self.rotational_step_size)
            semaphore.release()

    def _jog_ccw(self):
        semaphore = self.semaphores["MOTOR_PSI"]
        if semaphore.acquire(timeout=0.1):
            self.stage.psi.move_by(-self.rotational_step_size)
            semaphore.release()

    def _set_linear_jog_step(self):
        val = None
        while val is None:
            answer = input(f"Enter new step size or [ENTER] to cancel (current {self.linear_step_size}): ")
            if answer == "n":
                return
            try:
                val = float(answer)
            except ValueError:
                pass
        self.linear_step_size = val
        print(f"New step size set: {self.linear_step_size}")

    def _set_rotational_jog_step(self):
        val = None
        while val is None:
            answer = input(f"Enter new step size or [ENTER] to cancel (current {self.rotational_step_size}): ")
            if answer == "n":
                return
            try:
                val = float(answer)
            except ValueError:
                pass
        self.rotational_step_size = val
        print(f"New step size set: {self.rotational_step_size}")

    def _home(self):
        confirm = input("Are you sure you want to home? Type 'yes' to confirm: ")
        if confirm != "yes":
            return
        for semaphore in self.semaphores.values():
            semaphore.acquire()
        for motor in self.stage.motors:
            if motor:
                motor.home()
        for semaphore in self.semaphores.values():
            semaphore.release()
        log.info("Homing complete")

    def _help(self):
        print(f"""
        Stage Control
        -------------
        move left: {self.bindings.MOVE_LEFT}
        move right: {self.bindings.MOVE_RIGHT}
        move up: {self.bindings.MOVE_UP}
        move down: {self.bindings.MOVE_DOWN}
        move raise: {self.bindings.MOVE_RAISE}
        move lower: {self.bindings.MOVE_LOWER}
        jog left: {self.bindings.JOG_LEFT}
        jog right: {self.bindings.JOG_RIGHT}
        jog up: {self.bindings.JOG_UP}
        jog down: {self.bindings.JOG_DOWN}
        jog clockwise: {self.bindings.JOG_CLOCKWISE}
        jog counterclockwise: {self.bindings.JOG_COUNTERCLOCKWISE}
        linear jog step: {self.bindings.LINEAR_JOG_STEP}
        rotational jog step: {self.bindings.ROTATIONAL_JOG_STEP}
        home: {self.bindings.HOME}
        help: {self.bindings.HELP}
        quit: {self.bindings.QUIT}
        """)
        # stop all: {self.bindings.STOP_ALL}

    def loop(self) -> None:
        """
        Enters a blocking loop to control stage motion.
        """
        running = threading.Event()
        running.set()

        actions = list(self.bindings.dict().keys())
        keys = list(self.bindings.dict().values())
        funcs = {
            "MOVE_LEFT": self._move_left,
            "MOVE_RIGHT": self._move_right,
            "MOVE_UP": self._move_up,
            "MOVE_DOWN": self._move_down,
            "MOVE_RAISE": self._move_raise,
            "MOVE_LOWER": self._move_lower,
            "JOG_LEFT": self._jog_left,
            "JOG_RIGHT": self._jog_right,
            "JOG_UP": self._jog_up,
            "JOG_DOWN": self._jog_down,
            "JOG_CLOCKWISE": self._jog_cw,
            "JOG_COUNTERCLOCKWISE": self._jog_ccw,
            "LINEAR_JOG_STEP": self._set_linear_jog_step,
            "ROTATIONAL_JOG_STEP": self._set_rotational_jog_step,
            "HOME": self._home,
            "HELP": self._help,
        }
        flags = {binding : threading.Event() for binding in actions}

        # keyboard.add_hotkey(self.bindings.MOVE_LEFT, lambda: self._move_left(semaphores[self.bindings.MOVE_LEFT]))
        keyboard.add_hotkey(self.bindings.MOVE_LEFT, lambda: flags["MOVE_LEFT"].set())
        keyboard.add_hotkey(self.bindings.MOVE_RIGHT, lambda: flags["MOVE_RIGHT"].set())
        keyboard.add_hotkey(self.bindings.MOVE_UP, lambda: flags["MOVE_UP"].set())
        keyboard.add_hotkey(self.bindings.MOVE_DOWN, lambda: flags["MOVE_DOWN"].set())
        keyboard.add_hotkey(self.bindings.MOVE_RAISE, lambda: flags["MOVE_RAISE"].set())
        keyboard.add_hotkey(self.bindings.MOVE_LOWER, lambda: flags["MOVE_LOWER"].set())
        keyboard.add_hotkey(self.bindings.JOG_LEFT, lambda: flags["JOG_LEFT"].set())
        keyboard.add_hotkey(self.bindings.JOG_RIGHT, lambda: flags["JOG_RIGHT"].set())
        keyboard.add_hotkey(self.bindings.JOG_UP, lambda: flags["JOG_UP"].set())
        keyboard.add_hotkey(self.bindings.JOG_DOWN, lambda: flags["JOG_DOWN"].set())
        keyboard.add_hotkey(self.bindings.JOG_CLOCKWISE, lambda: flags["JOG_CLOCKWISE"].set())
        keyboard.add_hotkey(self.bindings.JOG_COUNTERCLOCKWISE, lambda: flags["JOG_COUNTERCLOCKWISE"].set())
        keyboard.add_hotkey(self.bindings.LINEAR_JOG_STEP, lambda: flags["LINEAR_JOG_STEP"].set())
        keyboard.add_hotkey(self.bindings.ROTATIONAL_JOG_STEP, lambda: flags["ROTATIONAL_JOG_STEP"].set())
        keyboard.add_hotkey(self.bindings.HOME, lambda: flags["HOME"].set())
        keyboard.add_hotkey(self.bindings.HELP, lambda: flags["HELP"].set())
        keyboard.add_hotkey(self.bindings.QUIT, lambda: running.clear())
        keyboard.add_hotkey(self.bindings.HELP, lambda: flags["HELP"].set())

        def run_flagged():
            for action, flag in flags.items():
                if flag.is_set():
                    t = threading.Thread(target=funcs[action], daemon=True)
                    t.start()
                    flag.clear()

        log.info("Entering keyboard control loop")
        while running.is_set():
            run_flagged()
            time.sleep(0.1)
        # else:
        # clean up all current running actions, make sure all semaphores are freed
