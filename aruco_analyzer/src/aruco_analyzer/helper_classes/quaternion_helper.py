# -*- coding: utf-8 -*-

# This file implements correct quaternion averaging.
#
# This method is computationally expensive compared to naive mean averaging.
# If only low accuracy is required (or the quaternions have similar orientations),
# then quaternion averaging can possibly be done through simply averaging the
# components.
#
# Based on:
#
# Markley, F. Landis, Yang Cheng, John Lucas Crassidis, and Yaakov Oshman.
# "Averaging quaternions." Journal of Guidance, Control, and Dynamics 30,
# no. 4 (2007): 1193-1197.
# Link: https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20070017872.pdf
#
# Code based on:
#
# Tolga Birdal. "averaging_quaternions" Matlab code.
# http://jp.mathworks.com/matlabcentral/fileexchange/40098-tolgabirdal-averaging-quaternions
#
# Comparison between different methods of averaging:
#
# Claus Gramkow. "On Averaging Rotations"
# Journal of Mathematical Imaging and Vision 15: 7–16, 2001, Kluwer Academic Publishers.
# https://pdfs.semanticscholar.org/ebef/1acdcc428e3ccada1a047f11f02895be148d.pdf
#
# Side note: In computer graphics, averaging or blending of two quaternions is often done through
# spherical linear interploation (slerp). Even though it's often used it might not be the best
# way to do things, as described in this post:
#
# Jonathan Blow.
# "Understanding Slerp, Then Not Using It", February 2004
# http://number-none.com/product/Understanding%20Slerp,%20Then%20Not%20Using%20It/
#

from __future__ import division

import math
import numpy as np
import numpy.matlib as npm
from pyquaternion import Quaternion
import cv2

def quaternion_distance(q1, q2, u='rad'):
    """
    returns angle between two quaternions
    """
    # rounding necessary because of values slightly greater than 1
    diff = math.acos(round(2*(q1[0]*q2[0]+q1[1]*q2[1]+q1[2]*q2[2]+q1[3]*q2[3])**2 - 1, 12))
    if u == 'deg':
        return math.degrees(diff)
    elif u == 'rad':
        return diff
    else:
        return diff

def quaternionToEuler(quat):
    quat = Quaternion(quat)
    return np.array(quat.yaw_pitch_roll)

def rodriguesToQuaternion(rod):
    dst, _ = cv2.Rodrigues(rod)
    return Quaternion(matrix=dst)

# Q is a Nx4 numpy matrix and contains the quaternions to average in the rows.
# The quaternions are arranged as (w,x,y,z), with w being the scalar
# The result will be the average quaternion of the input. Note that the signs
# of the output quaternion can be reversed, since q and -q describe the same orientation
def averageQuaternions(Q):
    # Number of quaternions to average
    M = Q.shape[0]
    A = npm.zeros(shape=(4,4))

    for i in range(0,M):
        q = Q[i,:]
        # multiply q with its transposed version q' and add A
        A = np.outer(q,q) + A

    # scale
    A = (1.0/M)*A
    # compute eigenvalues and -vectors
    eigenValues, eigenVectors = np.linalg.eig(A)
    # Sort by largest eigenvalue
    eigenVectors = eigenVectors[:,eigenValues.argsort()[::-1]]
    # return the real part of the largest eigenvector (has only real part)
    return np.real(eigenVectors[:,0].A1)


# Average multiple quaternions with specific weights
# The weight vector w must be of the same length as the number of rows in the
# quaternion maxtrix Q
def weightedAverageQuaternions(Q, w):
    # Number of quaternions to average
    M = Q.shape[0]
    A = npm.zeros(shape=(4,4))
    weightSum = 0

    for i in range(0,M):
        q = Q[i,:]
        A = w[i] * np.outer(q,q) + A
        weightSum += w[i]

    # scale
    A = (1.0/weightSum) * A

    # compute eigenvalues and -vectors
    eigenValues, eigenVectors = np.linalg.eig(A)

    # Sort by largest eigenvalue
    eigenVectors = eigenVectors[:,eigenValues.argsort()[::-1]]

    # return the real part of the largest eigenvector (has only real part)
    return np.real(eigenVectors[:,0].A1)
