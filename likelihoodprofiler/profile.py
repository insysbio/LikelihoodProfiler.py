import warnings

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
    """Short summary.

    It generates the profile function based on :code:`loss_func`. Used internally in methods :code:`"LIN_EXTRAPOL"`, :code:`"QUADR_EXTRAPOL"`.
    ----------
    theta_init : Array[Float64]
        starting values of parameter vector :math:`\\Theta`. The starting values is not necessary to be the optimum values for :code:`loss_func` but it the value of :code:`loss_func` must be lower than :code:`loss_crit`.
    theta_num : Int
        number :math:`n` of vector component to compute confidence interval :math:`\\Theta^n`.
    loss_func : Function
        loss function :math:`\\Lambda\\left(\\Theta\\right)` the profile of which is analyzed. Usually we use log-likelihood for profile analysis in form :math:`\\Lambda( \\theta ) = - 2 ln\\left( L(\\Theta) \\right)`.
    skip_optim : Bool
        set :code:`True` if you need marginal profile, i.e. profile without optimization. Default is :code:`False`.
    theta_bounds :Array[Array[Float64,Float64]]
        vector of bounds for each component in format :math:`(left_border, right_border)`. This bounds define the ranges for possible parameter values. The defaults are the non-limited values taking into account the :code:`scale`, i.e. :math:`(0, Inf)` for :code:`"log"` scale.
    local_alg : Function
        algorithm of optimization. Currently the local derivation free algorithms form NLOPT pack were tested. The methods: :code:`nlopt.LN_NELDERMEAD, nlopt.LN_COBYLA, nlopt.LN_PRAXIS` show good results. Methods: :code:`nlopt.LN_BOBYQA, nlopt.LN_SBPLX, nlopt.LN_NEWUOA` is not recommended.
    ftol_abs : Float64
         absolute tolerance criterion for profile function.
    **kwargs : Any
        the additional keyword arguments passed to :code:`get_right_endpoint` for specific :code:`method`.

    Returns
    -------
    Function
        Returns profile function for selected parameter component. Each call of the function
        starts optimization.

    """

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
                try:
                    loss = loss_func(theta_full)
                except ValueError:
                    warnings.warn("Error when call loss_func{}".format(theta_full), DeprecationWarning, stacklevel=2)
                    raise ValueError
                counter += 1
                return loss
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
