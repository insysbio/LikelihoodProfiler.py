import warnings
import math
import numpy as np
import nlopt

from .profile import profile

def get_right_endpoint_by_lin_extrapol(
    theta_init,  # initial point of parameters
    theta_num,  # number of parameter to scan
    loss_func,  # lambda(theta) - labmbda_min - delta_lambda
    # method, # function works only for method QUADR_EXTRAPOL

    theta_bounds=[],
    scan_bound=9.0,
    scan_tol=1e-3,
    loss_tol=0,  # 1e-3,
    # method args
    scan_hini=1,
    scan_hmax=np.inf,
    # local alg args
    local_alg=nlopt.LN_NELDERMEAD,
    max_iter=10**5,
    ftol_abs=1e-3,
    **kwargs  # options for local fitter
    ):
    if len(theta_bounds) == 0:
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
            warnings.warn("Close-to-zero parameters found when using :LN_NELDERMEAD.",  DeprecationWarning, stacklevel=2)
            print(np.where(zeroParameter))


    # to count loss function calls inside this function, accumulation
    accum_counter = 0
    # empty container
    pps = []

    prof = profile(
        theta_init,
        theta_num,
        loss_func,
        theta_bounds=theta_bounds,
        local_alg=local_alg,
        ftol_abs=loss_tol
    )

    # first iteration
    x_2 = theta_init[theta_num]
    theta_init_2 = theta_init
    iteration_count = 0

    # other iterations
    while True:
        global x_1  # not initialized for the first iteration
        global point_1  # not initialized for the first iteration
        iteration_count += 1  # to understand if this is a first iteration
        # get profile point
        point_2 = prof(
            x_2,
            theta_init_i=theta_init_2,  # hypothetically this makes optimization more effective
            maxeval=max_iter - accum_counter  # how many calls left
            )
        pps.append(point_2)
        accum_counter += point_2.counter # update counter
        if point_2.ret == 5:
            return [None, pps, "MAX_ITER_STOP"]
        elif point_2.ret == -5:
            return [None, pps, "LOSS_ERROR_STOP"]
        elif x_2 >= scan_bound and point_2.loss < 0.: # successfull result
            return [None, pps, "SCAN_BOUND_REACHED"]
        # no checking for the first iteration
        elif iteration_count>1 and (point_2.loss != point_1.loss) and math.isclose((x_2 - x_1) * point_2.loss / (point_2.loss - point_1.loss), 0, abs_tol = scan_tol): # successfull result
            return [x_2, pps, "BORDER_FOUND_BY_SCAN_TOL"]
        elif math.isclose(point_2.loss, 0., abs_tol = loss_tol): # successfull result
            return [x_2, pps, "BORDER_FOUND_BY_LOSS_TOL"]

        # next step
        if iteration_count == 1:
            x_3_extrapol = x_2 + scan_hini
        else:
            if (point_2.loss - point_1.loss) / (x_2 - x_1) <= 0:
                x_3_extrapol = x_2 + scan_hini
            else:
                x_3_extrapol = x_2 + (x_2 - x_1) * (0. - point_2.loss) / (point_2.loss - point_1.loss)

        x_3 = min([x_2+scan_hmax, x_3_extrapol, theta_bounds[theta_num][1]])
        # preparation for the next iteration
        point_1, x_1, x_2, theta_init_2 = point_2, x_2, x_3, point_2.params
