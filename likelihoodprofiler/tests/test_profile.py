import numpy as np
from pytest import approx

from .. import profile
from .cases_func import f_3p_1im_dep

def test_f_3p_1im_dep():
    prof = profile(
            [3., 2., 2.1],
            0,
            f_3p_1im_dep,
            skip_optim = False
    )
    x = np.arange(0,10,0.2)
    y = [prof(x[i]) for i in range(len(x))]
    assert y[4].value == approx(0.8)
    assert y[4].loss == approx(9.8402, abs=1e-3)
    assert y[4].ret == 3
    assert y[4].counter > 1
    assert len(y[4].params) == 3
