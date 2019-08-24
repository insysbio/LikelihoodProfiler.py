import numpy as np
import nlopt

from .cico_one_pass import get_right_endpoint_cico
from .get_right_endpoint_by_lin_extrapol import get_right_endpoint_by_lin_extrapol
from .method_quadr_extrapol import get_right_endpoint_by_quadr_extrapol


def get_right_endpoint(
    theta_init,  # initial point of parameters
    theta_num,  # number of parameter to scan
    loss_func,  # lambda(theta) - labmbda_min - delta_lambda
    method="CICO_ONE_PASS",
    theta_bounds=[],
    scan_bound=9.0,
    scan_tol=1e-3,
    loss_tol=None,  # 1e-3,
    # method args
    scan_hini=1.,
    scan_hmax=np.inf,
    # local alg args
    local_alg=nlopt.LN_NELDERMEAD,
    max_iter=10**5,
    ftol_abs=1e-3,
    **kwargs  # options for local fitter
):
    if method == "CICO_ONE_PASS":
        if loss_tol is None:
            loss_tol = 1e-3
        return get_right_endpoint_cico(
            theta_init,
            theta_num,
            loss_func,
            theta_bounds,
            scan_bound,
            scan_tol,
            loss_tol,
            max_iter,
            local_alg,
            **kwargs
        )
    elif method == "LIN_EXTRAPOL":
        if loss_tol is None:
            loss_tol = 0
        return get_right_endpoint_by_lin_extrapol(
            theta_init,
            theta_num,
            loss_func,
            theta_bounds,
            scan_bound,
            scan_tol,
            loss_tol,
            scan_hini,
            scan_hmax,
            local_alg,
            max_iter,
            ftol_abs,
            **kwargs
        )
    elif method == "QUADR_EXTRAPOL":
        if loss_tol is None:
            loss_tol = 0
        return get_right_endpoint_by_quadr_extrapol(
            theta_init,
            theta_num,
            loss_func,
            theta_bounds,
            scan_bound,
            scan_tol,
            loss_tol,
            scan_hini,
            scan_hmax,
            local_alg,
            max_iter,
            ftol_abs,
            **kwargs
        )
    else:
        raise ValueError("Unknown method")
