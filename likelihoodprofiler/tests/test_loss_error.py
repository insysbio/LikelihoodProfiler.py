#import math
from pytest import approx, raises
import numpy

from .. import get_endpoint, profile
#import unittest
import nlopt

def err_fun_generate():
    counter = 0
    def fun(x):
        nonlocal counter
        counter +=1
        if counter > 5:
            raise ValueError
        return 5.0 + (x[0]-3.0)**2 + (x[1]-4.0)**2
    return fun

def test_loss_error_cico():
    err_func = err_fun_generate()
    res0 = get_endpoint(
        [3., 4.],
        1,
        err_func,
        "CICO_ONE_PASS",
        loss_crit = 9.
    )
    assert res0.value == None
    assert len(res0.profilePoints) == 0
    assert res0.status == 'LOSS_ERROR_STOP'
    assert res0.counter < 5
    assert type(res0.supreme) == numpy.float64

def test_profile_error():
    err_func = err_fun_generate()
    prof = profile(
        [3., 4.],
        1,
        err_func
    )
    #with raises(nlopt.ForcedStop):
    #    res0 = prof(5.)
    res0 = prof(5.)
    assert res0.ret == -5
    assert res0.counter == 5

def test_loss_error_lin():
    err_func = err_fun_generate()
    res0 = get_endpoint(
        [3., 4.],
        1,
        err_func,
        "LIN_EXTRAPOL",
        loss_crit = 9.
    )
    assert res0.value == None
    assert len(res0.profilePoints) == 1
    assert res0.status == 'LOSS_ERROR_STOP'
    assert res0.counter < 5
    assert type(res0.supreme) == numpy.float64
    pp = res0.profilePoints[0]
    assert pp.ret == -5

def test_loss_error_lin():
    err_func = err_fun_generate()
    res0 = get_endpoint(
        [3., 4.],
        1,
        err_func,
        "QUADR_EXTRAPOL",
        loss_crit = 9.
    )
    assert res0.value == None
    assert len(res0.profilePoints) == 1
    assert res0.status == 'LOSS_ERROR_STOP'
    assert res0.counter < 5
    assert type(res0.supreme) == numpy.float64
    pp = res0.profilePoints[0]
    assert pp.ret == -5
