# coding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
__metaclass__ = type

from pyoptflow import utils
from pyoptflow.core import extract_motion_proesmans
from pyoptflow.extrapolation import semilagrangian


def read_rainrate(filename):
    return


def filter_rr(rr):
    """filtered version of data"""
    return rr


def rr2ubyte(rr, R_min=0.05, R_max=10.0, filter_stddev=3.0):
    return utils.rainfall_to_ubyte(rr, R_min=R_min, R_max=R_max,
                                   filter_stddev=filter_stddev)


def motion(rr0ubyte, rr1ubyte, lam=25.0, num_iter=250, num_levels=6):
    return extract_motion_proesmans(rr0ubyte, rr1ubyte, lam=lam,
                                    num_iter=num_iter,
                                    num_levels=num_levels)[0]


def extrapolate(rr, v, t, n_steps=15, n_iter=3, inverse=True):
    return semilagrangian(rr, v, t, n_steps=n_steps, n_iter=n_iter,
                          inverse=inverse)

