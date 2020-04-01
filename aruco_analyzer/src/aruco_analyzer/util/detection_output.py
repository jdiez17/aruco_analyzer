#!/usr/bin/env python
import numpy as np
import time
from .quaternion_helper import *


class DetectionOutput (object):
    """
    This class will be used for capsuling the output data.
    """

    def __init__(self):
        self._camera_image = None
        self.ar_ids = []
        self.positions = []
        self.quaternions = []
        self.timestamp = None
        self._marker_types = []

    def pack_dummy(self, camera_image):
        self._camera_image = camera_image
        self.ar_ids = np.array([0])
        self._marker_types = ['0']
        self.positions.append(np.array([0, 0, 0]))
        self.quaternions.append(np.array([0, 0, 0, 1]))
        self.timestamp = time.time()

    def pack(self, camera_image, ar_ids, rvecs, tvecs, marker_type):
        self._camera_image = camera_image
        self.ar_ids = ar_ids
        self._marker_types = marker_type

        for rvec, tvec in zip(rvecs, tvecs):
            self.positions.append(tvec)
            self.quaternions.append(rodriguesToQuaternion(rvec).elements)
        self.timestamp = time.time()

    def append(self, detection):
        if detection is None:
            return

        if self._camera_image is None:
            self._camera_image = detection._camera_image
            self.timestamp = time.time()

            self.ar_ids = detection.ar_ids
            self.quaternions = detection.quaternions
            self.positions = detection.positions
            self._marker_types = detection._marker_types
        else:
            self.ar_ids = np.concatenate((self.ar_ids, detection.ar_ids))
            self.quaternions = np.concatenate((self.quaternions, detection.quaternions))
            self.positions = np.concatenate((self.positions, detection.positions))
            self._marker_types = np.concatenate((self._marker_types, detection._marker_types))

    def get_single_output(self, index):
        single_output = SingleOutput()
        single_output.pack_from_parent(self, index)
        return single_output


class SingleOutput (object):
    def __init__(self):
        self._ar_id = None
        self._position = None
        self._quaternion = None
        self._timestamp = None
        self._marker_type = None

    def pack_from_parent(self, parent, index):
        self._parent = parent
        self._camera_image = parent._camera_image
        self._ar_id = parent.ar_ids[index]
        self._position = parent.positions[index]
        self._quaternion = parent.quaternions[index]
        self._timestamp = parent.timestamp
        self._marker_type = parent._marker_types[index]

    @property
    def parent(self):
        return self._parent

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = np.copy(value)

    @property
    def quaternion(self):
        return self._quaternion

    @quaternion.setter
    def quaternion(self, value):
        self._quaternion = np.copy(value)

    @property
    def euler(self):
        return quaternionToEuler(self._quaternion)

    @property
    def rotation(self):
        return self._rotation

    @property
    def ar_id(self):
        return self._ar_id

    @ar_id.setter
    def ar_id(self, value):
        self._ar_id = value

    @property
    def unique_ar_id(self):
        return '{}{:03d}'.format(self.marker_type, self.ar_id)

    # def get_unique_ar_id_string(self):
    #     """
    #     Returns a (hopefully) unique string for this id.
    #     Id is generated by (M|B)XXX, where XXX is the marker of the id (of the first marker in the board)
    #     """
    #     assert(self.marker_type is not None)

    #     return '{}{:03d}'.format(self.marker_type, self.ar_id)

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def marker_type(self):
        return self._marker_type

    @marker_type.setter
    def marker_type(self, value):
        self._marker_type = value

    @property
    def camera_image(self):

        return self._camera_image

    @camera_image.setter
    def camera_image(self, value):
        self._camera_image = value

    def toCSV(self):
        separator = ','
        pos = separator.join(map(str, self.position.tolist()))
        ori = separator.join(map(str, self.quaternion))
        out = separator.join([self.unique_ar_id, pos, ori])
        return out
