import numpy as np
import nlopt

from .support_math_func import scaling, unscaling
from .structures import ProfilePoint, EndPoint
from .get_right_endpoint import get_right_endpoint


def get_endpoint(
    theta_init,
    theta_num,
    loss_func,
    method,
    direction="right",
    loss_crit=0.0,
    scale=[],
    theta_bounds=[],
    scan_bound=None,
    scan_tol=1e-3,
    loss_tol=1e-3,
    local_alg=nlopt.LN_NELDERMEAD,
    **kwargs):
    """Calculates right or left endpoint of CI for parameter component. It is a wripper
    of `get_right_endpoint` functions for selection of direction and using different
    transformations for faster optimization.

    Parameters
    ----------
    theta_init : Array[Float64]
        starting values of parameter vector :math:`\\Theta`. The starting values is not necessary to be the optimum values for :code:`loss_func` but it the value of :code:`loss_func` must be lower than :code:`loss_crit`.
    theta_num : Int
        number :math:`n` of vector component to compute confidence interval :math:`\\Theta^n`.
    loss_func : Function
        loss function :math:`\\Lambda\\left(\\Theta\\right)` the profile of which is analyzed. Usually we use log-likelihood for profile analysis in form :math:`\\Lambda( \\theta ) = - 2 ln\\left( L(\\Theta) \\right)`.
    method : String
        computational method to evaluate interval endpoint. Currently the following methods are implemented: :code:`"CICO_ONE_PASS"`, :code:`"LIN_EXTRAPOL"`, :code:`"QUADR_EXTRAPOL"`.
    direction : String
        :code:`"right"` or :code:`"left"` endpoint to estimate.
    loss_crit : Float64
        critical level of loss function. The endpoint of CI for selected parameter is the value at which profile likelihood meets the value of :code:`loss_crit`.
    scale : String
        vector of scale transformations for each component. Possible values: :code:`"direct", "log", "logit"`. This option can make optimization much more faster, especially for wide :code:`theta_bounds`. The default value is :code:`"direct"` (no transformation) for all components.
    theta_bounds :Array[Array[Float64,Float64]]
        vector of bounds for each component in format :math:`(left_border, right_border)`. This bounds define the ranges for possible parameter values. The defaults are the non-limited values taking into account the :code:`scale`, i.e. :math:`(0, Inf)` for :code:`"log"` scale.
    scan_bounds : Array[Float64,Float64]
         vector of scan bound for :code:`theta_num` component. It must be within the :code:`theta_bounds` for the scanned component. The defaults are `(-9., 9.) for transformed values, i.e. :math:`(1e-9, 1e9)` for :code:`"log"` scale.
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
    class EndPoint
         object storing confidence endpoint and profile points found on fly.

    """
    if len(scale) == 0:
        scale = np.tile("direct", len(theta_init))

    if len(theta_bounds) == 0:
        theta_bounds = unscaling(
            np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1)),
            )

    if scan_bound is None:
        x = -9.0 if (direction == "left") else 9.0
        scan_bound = unscaling(x, scale[theta_num])

    isLeft = direction == "left"

    # checking arguments
    # theta_bound[1] < theta_init < theta_bound[2]
    theta_init_outside_theta_bounds = [not(theta_bounds[i][0] < theta_init[i] < theta_bounds[i][1])
                                       for i in range(len(theta_init))]
    if any(theta_init_outside_theta_bounds):
        raise BaseException("theta_init is outside theta_bound: {}".format(np.where(theta_init_outside_theta_bounds)))

    # scan_bound should be within theta_bounds
    if (not(theta_bounds[theta_num][0]) < scan_bound < theta_bounds[theta_num][1]):
        raise ValueError("scan_bound are outside of the theta_bounds {}".format(theta_bounds[theta_num]))

    # theta_init should be within scan_bound
    if (theta_init[theta_num] >= scan_bound
        and not(isLeft)) or (theta_init[theta_num] <= scan_bound and isLeft):
        raise ValueError("init values are outside of the scan_bound {}".format(scan_bound))

    # 0 <= theta_bound[1] for :log
    less_than_zero_theta_bounds = all(i == "log" for i in scale) \
                                  and [theta_bounds[i][0] < 0 for i in range(len(theta_init))]
    if less_than_zero_theta_bounds and any(less_than_zero_theta_bounds):
        raise ValueError(":log scaled theta_bound min is negative: {}".format(np.where(less_than_zero_theta_bounds)))

    # 0 <= theta_bounds <= 1 for :logit
    less_than_zero_theta_bounds = all(i == "logit" for i in scale) \
                                  and [theta_bounds[i][1] < 0 or theta_bounds[i][2] > 1 for i in range(len(theta_init))]
    if less_than_zero_theta_bounds and any(less_than_zero_theta_bounds):
        raise ValueError(":logit scaled theta_bound min is outside range [0,1]: {}".format({np.where(less_than_zero_theta_bounds)}))


    # loss_func(theta_init) < loss_crit
    if (not(loss_func(theta_init) < loss_crit)):
        raise ValueError("Check theta_init and loss_crit: loss_func(theta_init) should be < loss_crit")

    # set counter in the scope
    counter = 0

    # transforming
    n_scale = len(scale)

    theta_init_gd = map(lambda i: scaling(theta_init[i], scale[i]), range(n_scale))
    theta_init_gd = list(theta_init_gd)

    if isLeft:
        theta_init_gd[theta_num] *= -1  # change direction

    def loss_func_gd(theta_gd):
        nonlocal counter
        nonlocal scale
        theta_g = np.copy(theta_gd)
        if isLeft:
            theta_g[theta_num] *= -1  # change direction

        theta = map(lambda i: unscaling(theta_g[i], scale[i]), range(n_scale))
        theta = list(theta)

        # update counter
        counter += 1
        # calculate function
        return loss_func(theta) - loss_crit

    theta_bounds_gd = map(
        lambda i: [scaling(theta_bounds[i][0], scale[i]),
                   scaling(theta_bounds[i][1], scale[i])
                   ],
        range(n_scale))
    theta_bounds_gd = list(theta_bounds_gd)

    if isLeft:
        theta_bounds_gd[theta_num] = (-1*theta_bounds_gd[theta_num][1], -1*theta_bounds_gd[theta_num][0]) # ??? # change direction

    scan_bound_gd = scaling(scan_bound, scale[theta_num])
    if isLeft:
         scan_bound_gd *= -1  # change direction

    # calculate endpoint using base method
    optf_gd, pp_gd, status = get_right_endpoint(
        theta_init_gd,
        theta_num,
        loss_func_gd,
        method,
        theta_bounds = theta_bounds_gd,
        scan_bound = scan_bound_gd,
        scan_tol = scan_tol,
        loss_tol = loss_tol,
        local_alg = local_alg,
        **kwargs
    )

    # transforming back
    if (isLeft and not(optf_gd is None)):
        optf_gd *= -1  # change direction
    optf = unscaling(optf_gd, scale[theta_num])

    def temp_fun(pp):
        if isLeft:
             pp.params[theta_num] *= -1 # change direction
        return ProfilePoint(
            unscaling(pp.params[theta_num], scale[theta_num]),
            pp.loss + loss_crit,
            list(map(lambda i: unscaling(theta_init, i), scale)), # ??? Этот момент переписать
            pp.ret,
            pp.counter
        )
    pps = [temp_fun(pp_gd[i]) for i in range(len(pp_gd))]

    return EndPoint(optf, pps, status, direction, counter)
