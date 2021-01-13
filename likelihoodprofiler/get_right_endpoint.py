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
    """Interface for current and future methods for endpoint estimation.

    Parameters
    ----------
    theta_init : Array[Flaot64]
        `theta_init`: starting values of parameter vector :math:`\\Theta`. The starting values is not necessary to be the optimum values for :code:`loss_func` but it the value of :code:`loss_func` must be lower than :code:`loss_crit`.
    theta_num : Int
        number :math:`n` of vector component to compute confidence interval :math:`\\Theta^n`.
    loss_func : Function
        loss function the profile of which is analyzed, see :code:`get_interval`. In this :code:`function loss` crit is always equal 0 for code simplification.
    method : String
        this value is always fixed. Implemented methods are: :code:`"CICO_ONE_PASS"`. It is implemented for easy switching between different implemented and future methods.
    theta_bounds : Array[Array[Float64, Float64]]
        vector of bounds for each component in format :math:`(left_bound, right_bound)`. This bounds define the ranges for possible parameter values.
    scan_bound : Float64
        right scan bound for :code:`theta_num` component. It must be within the :code:`theta_bounds` for the scanned component.
    scan_tol : Float64
        Absolute tolerance of scanned component (stop criterion).
    loss_tol : Float64
        Absolute tolerance of :code:`loss_func` at :code:`loss_crit` (stop criterion). *Restriction*. Currently is not effective for :code:`nlopt.CICO_ONE_PASS` methods because of limitation in :code:`nlopt.LN_AUGLAG` interface.
    local_alg : Function
        algorithm of optimization. Currently the local derivation free algorithms form NLOPT pack were tested. The methods: :code:`nlopt.LN_NELDERMEAD, nlopt.LN_COBYLA, nlopt.LN_PRAXIS` show good results. Methods: :code:`nlopt.LN_BOBYQA, nlopt.LN_SBPLX, nlopt.LN_NEWUOA` is not recommended.
    **kwargs : Any
        the additional keyword arguments passed to :code:`get_right_endpoint` for specific :code:`method`.

    Returns
    -------
    Array
        * Right end point value: :code:`Float64`.
        * Profile points estimated on fly: :code:`Array[ ProfilePoint, 1]`
        * Status of sulution: :code:`String`. One of values: :code:`"BORDER_FOUND_BY_SCAN_TOL"`, :code:`"SCAN_BOUND_REACHED"`.
    """
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
