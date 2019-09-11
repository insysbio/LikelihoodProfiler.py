import math
import warnings

import numpy as np
import nlopt

from .structures import ProfilePoint


def get_right_endpoint_cico(
    theta_init,  # initial point of parameters
    theta_num,  # number of parameter to scan
    loss_func,  # lambda(theta) - labmbda_min - delta_lambda
    theta_bounds=None,
    scan_bound=9.0,
    scan_tol=1e-3,
    loss_tol=1e-3,
    max_iter=10**5,
    local_alg=nlopt.LN_NELDERMEAD,
    **kwargs
    ):
    # checking arguments
    if (theta_bounds is None):
        theta_bounds = np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1))

    if theta_num > len(theta_init):
        raise ValueError('theta_num {0} exceed theta dimention'.format(theta_num))

    def scan_func(theta):
        nonlocal theta_num
        return theta[theta_num]

    return get_right_endpoint_cico_with_scan_func(
        theta_init,
        loss_func,
        scan_func,
        theta_bounds=theta_bounds,
        scan_bound=scan_bound,
        scan_tol=scan_tol,
        loss_tol=loss_tol,
        max_iter=max_iter,
        local_alg=local_alg,
        **kwargs
    )


def get_right_endpoint_cico_with_scan_func(
    theta_init,  # initial point of parameters
    loss_func,  # lambda(theta) - labmbda_min - delta_lambda
    scan_func,  # h(theta) function for predictions or parameters
    theta_bounds=None,
    scan_bound=9.0,
    scan_tol=1e-3,
    loss_tol=1e-3,  # i do not know how to use it
    # good results in :LN_NELDERMEAD, :LN_COBYLA, :LN_PRAXIS,
    # errors in :LN_BOBYQA, :LN_SBPLX, :LN_NEWUOA
    local_alg=nlopt.LN_NELDERMEAD,
    # options for local fitter :max_iter
    # ftol_abs=1e-3,
    max_iter=10**5,
    **kwargs
):
    if (theta_bounds is None):
        theta_bounds = np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1))

    # dim of the theta vector
    n_theta = len(theta_init)

    # checking arguments
    # methods which are not supported
    if local_alg in [nlopt.LN_BOBYQA, nlopt.LN_SBPLX, nlopt.LN_NEWUOA]:
        warnings.warn("Using current local_alg may result in wrong output.",  DeprecationWarning, stacklevel=2)

    # when using :LN_NELDERMEAD initial parameters should not be zero
    if local_alg == nlopt.LN_NELDERMEAD:
        zeroParameter = [math.isclose(theta_init[i], 0., abs_tol=1e-2) for i in range(n_theta)]
        if any(zeroParameter):
            warnings.warn("Close-to-zero parameters found when using LN_NELDERMEAD.", DeprecationWarning, stacklevel=2)
            print(np.where(zeroParameter))

    # optimizer
    local_opt = nlopt.opt(local_alg, n_theta)
    local_opt.set_ftol_abs(scan_tol)  # ftol_abs

    # Constraints function
    out_of_bound = False
    def constraints_func(x, g):
        nonlocal out_of_bound
        try:
            loss = loss_func(x)
        except ValueError:
            warnings.warn("Error when call loss_func{}".format(x), DeprecationWarning, stacklevel=2)
            raise ValueError

        if (loss < 0) and (scan_func(x) > scan_bound):
            out_of_bound = True
            raise nlopt.ForcedStop("Out of the scan bound but in ll constraint.")
        else:
            return loss

    # constrain optimizer
    opt = nlopt.opt(nlopt.LN_AUGLAG, n_theta)
    opt.set_ftol_abs(scan_tol)
    opt.set_max_objective(lambda x, g: scan_func(x))
    """
    lb = [theta_bounds[i][0] for i in range(n_theta)]  # minimum.(theta_bounds)
    ub = [theta_bounds[i][1] for i in range(n_theta)]  # maximum.(theta_bounds)
    opt.set_lower_bounds(lb)
    opt.set_upper_bounds(ub)
    """
    opt.set_local_optimizer(local_opt)
    opt.set_maxeval(max_iter)

    # inequality constraints
    opt.add_inequality_constraint(constraints_func, loss_tol)
    for i in range(n_theta):
        opt.add_inequality_constraint(lambda x, g: x[i] - theta_bounds[i][1], 0)
    for i in range(n_theta):
        opt.add_inequality_constraint(lambda x, g: theta_bounds[i][0] - x[i], 0)
    # start optimization
    try:
        optx = opt.optimize(theta_init)
        optf = opt.last_optimum_value()
        ret = opt.last_optimize_result()
    except nlopt.ForcedStop:
        ret = -5

    if ret == -5 and not out_of_bound:
        pp = []
        res = [None, pp, "LOSS_ERROR_STOP"]
    elif ret == 5:
        pp = []
        res = [None, pp, "MAX_ITER_STOP"]
    elif ret == -5 and out_of_bound:
        pp = []
        res = [None, pp, "SCAN_BOUND_REACHED"]
    elif ret == 3:
        loss = loss_func(optx)
        pp = [ProfilePoint(optf, loss, optx, ret, None)]
        res = [optf, pp, "BORDER_FOUND_BY_SCAN_TOL"]
    else:
        raise ValueError("No interpretation of the optimization results.")

    return res
