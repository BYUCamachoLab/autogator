# -*- coding: utf-8 -*-
#
# Copyright © Simphony Project Contributors
# Licensed under the terms of the MIT License
# (see simphony/__init__.py for details)

"""
autogator.models.motioncontrol
==============================

This module contains the classes for modeling the state, position, and/or
motion of the chip stage (but not actually controlling it, as this is a model
class, not a controller).
"""


import numpy as np
from PySide2.QtCore import QObject, Signal


class LinearMotor(QObject):
    """
    A motor with a linear travel.

    Attributes
    ----------
    position : int
    velocity : int
    jog_size : int

    Parameters
    ----------
    max_pos : int
    min_pos : int
    position : int
    reverse : bool
        False if the stage's position increases in the same direction as the
        coordinate system. True if opposite.
    max_vel : int
    min_vel : int
    velocity : int
    max_jog : int
    min_jog : int
    jog_size : int
    """
    position_changed = Signal(int)
    velocity_changed = Signal(int)
    jog_size_changed = Signal(int)

    def __init__(
        self,
        max_pos=0,
        min_pos=0,
        position=0,
        reverse=False,
        max_vel=0,
        min_vel=0,
        velocity=0,
        max_jog=0,
        min_jog=0,
        jog_size=0,
    ):
        super().__init__()
        self.max_pos = max_pos
        self.min_pos = min_pos
        self._position = position
        self.reverse = reverse
        self.max_vel = max_vel
        self.min_vel = min_vel
        self._velocity = velocity
        self.max_jog = max_jog
        self.min_jog = min_jog
        self._jog_size = jog_size

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        self.position_changed.emit(value)

    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, value):
        self._velocity = value
        self.velocity_changed.emit(value)

    @property
    def jog_size(self):
        return self._jog_size

    @jog_size.setter
    def jog_size(self, value):
        self._jog_size = value
        self.jog_size_changed.emit(value)


class RotationalMotor(QObject):
    def __init__(self):
        super().__init__()


class CompositeStage:
    """
    A CompositeStage is a collection of motors working in harmony to control
    the motion of a single object or surface.
    """

    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0
        self.pos_z = 0
        self.rotation = 0

    @property
    def state(self):
        return np.array([[self.pos_x], [self.pos_y], [self.pos_z], [self.rotation],])

    @state.setter
    def state(self, state):
        if state.shape != self.state.shape:
            raise ValueError
        self.pos_x = state.item(0)
        self.pos_y = state.item(1)
        self.pos_z = state.item(2)
        self.rotation = state.item(3)
