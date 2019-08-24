import nlopt
import numpy as np

from .structures import ProfilePoint


def profile(
    theta_init,
    theta_num,
    loss_func,
    skip_optim=False,
    theta_bounds=None,
    local_alg=nlopt.LN_NELDERMEAD,
    ftol_abs=1e-3,
     **kwargs
):

    if theta_bounds is None:
        theta_bounds = np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1))

    theta_length = len(theta_init)

    # set indexes
    indexes_rest = np.arange(0, theta_length, 1)
    indexes_rest = np.delete(indexes_rest, theta_num)

    # set bounds
    lb = [theta_bounds[i][0] for i in indexes_rest]
    ub = [theta_bounds[i][1] for i in indexes_rest]
    if skip_optim or theta_length == 1:
        def profileFuncSkipOptim(x, theta_init_i=theta_init, maxeval=10**5):
            nonlocal theta_init
            theta_full = theta_init_i[0:theta_num] + [x] + theta_init_i[theta_num+1:len(theta_init_i)]
            loss = loss_func(theta_full)
            return ProfilePoint(
                x,
                loss,
                theta_full,
                1,  # OPTIMIZATION_SKIPPED
                1
            )
        return profileFuncSkipOptim
    else:
        opt = nlopt.opt(local_alg, theta_length - 1)
        opt.set_ftol_abs(ftol_abs)
        opt.set_lower_bounds(lb)
        opt.set_upper_bounds(ub)


        def profileFunc(x, theta_init_i = theta_init, maxeval = 10**5):
            counter = 0
            theta_init_rest = np.delete(theta_init_i, theta_num)

            def loss_func_rest(theta_rest, g):
                nonlocal counter
                theta_full = np.concatenate((theta_rest[0:theta_num], [x], theta_rest[theta_num:len(theta_rest)]), axis=0)
                counter += 1
                return loss_func(theta_full)
            # set optimizer
            opt.set_min_objective(loss_func_rest)
            opt.set_maxeval(maxeval)
            # start optimization
            theta_opt = opt.optimize(theta_init_rest)
            loss = opt.last_optimum_value()
            ret = opt.last_optimize_result()
            theta_opt = np.concatenate((theta_opt[0:theta_num], [x], theta_opt[theta_num:]), axis=0)
            return ProfilePoint(
                x,
                loss,
                theta_opt,
                ret,
                counter
            )
        return profileFunc
