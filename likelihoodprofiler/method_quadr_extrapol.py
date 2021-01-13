import warnings
import math
import numpy as np
import nlopt

from .profile import profile
from .support_math_func import unscaling


def get_right_endpoint_by_quadr_extrapol(
    theta_init,  # initial point of parameters
    theta_num,  # number of parameter to scan
    loss_func,  # lambda(theta) - labmbda_min - delta_lambda
    theta_bounds=[],
    scan_bound=9.0,
    scan_tol=1e-3,
    loss_tol=0, # 1e-3,
    # method args
    scan_hini=1.,
    scan_hmax=np.inf,
    # local alg args
    local_alg=nlopt.LN_NELDERMEAD,
    max_iter=10**5,
    ftol_abs=1e-3,
    **kwargs # options for local fitter
):
    if len(theta_bounds) == 0:
        theta_bounds = unscaling(
            np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1)),
        )

    # dim of the theta vector
    n_theta = len(theta_init)

    # checking arguments
    # methods which are not supported
    if local_alg in [nlopt.LN_BOBYQA, nlopt.LN_SBPLX, nlopt.LN_NEWUOA]:
        warnings.warn("Using current local_alg may result in wrong output.",  DeprecationWarning, stacklevel=2) # ??? Как выводить название алгоритма

    # when using :LN_NELDERMEAD initial parameters should not be zero
    if local_alg == nlopt.LN_NELDERMEAD:
        zeroParameter = [math.isclose(theta_init[i], 0., abs_tol=1e-2) for i in range(n_theta)]
        if any(zeroParameter):
            warnings.warn("Close-to-zero parameters found when using :LN_NELDERMEAD.")
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
    x_3 = theta_init[theta_num]
    theta_init_3 = theta_init
    iteration_count = 0

    # other iterations
    while True:
        # preparation
        global x_2  # not initialized for the first iteration
        global x_1  # not initialized for the first iteration
        global point_2  # not initialized for the first iteration
        global point_1  # not initialized for the first iteration
        iteration_count += 1  # to understand if this is a first iteration

        # get profile point
        point_3 = prof(
            x_3,
            theta_init_i=theta_init_3, # hypothetically this makes optimization more effective
            maxeval=max_iter - accum_counter # how many calls left
            )
        pps.append(point_3)
        accum_counter += point_3.counter # update counter
        if point_3.ret == 5:
            return [None, pps, "MAX_ITER_STOP"] # break
        elif point_3.ret == -5:
            return [None, pps, "LOSS_ERROR_STOP"]
        elif x_3 >= scan_bound and point_3.loss < 0.:
            return [None, pps, "SCAN_BOUND_REACHED"] # break
        # no checking for the first and second iterations
        # elseif iteration_count>2 && isapprox(x_3, x_2, atol = scan_tol)
        elif iteration_count>1 and point_3.loss != point_2.loss and math.isclose((x_3 - x_2) * point_3.loss / (point_3.loss - point_2.loss), 0., abs_tol = scan_tol):
            return [x_3, pps, "BORDER_FOUND_BY_SCAN_TOL"] # break
        elif math.isclose(point_3.loss, 0, abs_tol=loss_tol):
            return [x_3, pps, "BORDER_FOUND_BY_LOSS_TOL"] # break
        # next step
        if iteration_count == 1:
            x_4_extrapol = x_3 + scan_hini
            x_4 = min([x_3+scan_hmax, x_4_extrapol, theta_bounds[theta_num][1]])
            point_2, x_2, x_3, theta_init_3 = point_3, x_3, x_4, point_3.params
        elif iteration_count == 2:
            D = [
                [x_3**2, x_3, 1],
                [x_2**2, x_2, 1],
                [2**x_2, 1, 0]
                ]
            Da = [
                [point_3.loss, x_3, 1],
                [point_2.loss, x_2, 1],
                [0, 1, 0]
                ]
            Db = [
                [x_3**2, point_3.loss, 1],
                [x_2**2, point_2.loss, 1],
                [2*x_2, 0, 0]
                ]
            Dc = [
                [x_3**2, x_3, point_3.loss],
                [x_2**2, x_2, point_2.loss],
                [2*x_2, 1, 0]
                ]
            a = np.linalg.det(Da) / np.linalg.det(D)
            b = np.linalg.det(Db) / np.linalg.det(D)
            c = np.linalg.det(Dc) / np.linalg.det(D)
            if a <= 0:
                x_4_extrapol = x_3 + scan_hini
            else:
                x_4_extrapol = (-b + math.sqrt(b**2-4*a*c))/2/a

            x_4 = min([x_3+scan_hmax, x_4_extrapol, theta_bounds[theta_num][1]])
            x_1, x_2, x_3, point_1, point_2, theta_init_3 = x_2, x_3, x_4, point_2, point_3, point_3.params
        else:
            D = [
                [x_3**2, x_3, 1],
                [x_2**2, x_2, 1],
                [x_1**2, x_1, 1]
                ]
            Da = [
                [point_3.loss, x_3, 1],
                [point_2.loss, x_2, 1],
                [point_1.loss, x_1, 1]
                ]
            Db = [
                [x_3**2, point_3.loss, 1],
                [x_2**2, point_2.loss, 1],
                [x_1**2, point_1.loss, 1]
                ]
            Dc = [
                [x_3**2, x_3, point_3.loss],
                [x_2**2, x_2, point_2.loss],
                [x_1**2, x_1, point_1.loss]
                ]
            a = np.linalg.det(Da) / np.linalg.det(D)
            b = np.linalg.det(Db) / np.linalg.det(D)
            c = np.linalg.det(Dc) / np.linalg.det(D)
            if (a <= 0) or (b**2-4*a*c < 0):
                x_4_extrapol = x_3 + scan_hini
            else:
                x_4_extrapol = (-b + math.sqrt(b**2-4*a*c))/2/a

            x_4 = min([x_3+scan_hmax, x_4_extrapol, theta_bounds[theta_num][1]])
            x_1, x_2, x_3, point_1, point_2, theta_init_3 = x_2, x_3, x_4, point_2, point_3, point_3.params
