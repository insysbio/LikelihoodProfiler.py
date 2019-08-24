import numpy as np
import nlopt

from .support_math_func import scaling, unscaling
from .structures import ProfilePoint, EndPoint
from .get_right_endpoint import get_right_endpoint

"""
    function get_endpoint(
        theta_init::Vector{Float64},
        theta_num::Int,
        loss_func::Function,
        method::Symbol,
        direction::Symbol = :right;

        loss_crit::Float64 = 0.0,
        scale::Vector{Symbol} = fill(:direct, length(theta_init)),
        theta_bounds::Vector{Tuple{Float64,Float64}} = unscaling.(
            fill((-Inf, Inf), length(theta_init)),
            scale
            ),
        scan_bound::Float64 = unscaling(
            (direction==:left) ? -9.0 : 9.0,
            scale[theta_num]
            ),
        scan_tol::Float64 = 1e-3,
        loss_tol::Float64 = 1e-3,
        local_alg::Symbol = :LN_NELDERMEAD,
        kwargs...
        )

Calculates right or left endpoint of CI for parameter component. It is a wripper
of `get_right_endpoint` functions for selection of direction and using different
transformations for faster optimization.

## Return
[`EndPoint`](@ref) object storing confidence endpoint and profile points found on fly.

## Arguments
- `theta_init`: starting values of parameter vector ``\\theta``. The starting values is not necessary to be the optimum values for `loss_func` but it the value of `loss_func` must be lower than `loss_crit`.
- `theta_num`: number ``n`` of vector component to compute confidence interval ``\\theta^n``.
- `loss_func`: loss function ``\\Lambda\\left(\\theta\\right)`` the profile of which is analyzed. Usually we use log-likelihood for profile analysis in form ``\\Lambda( \\theta ) = - 2 ln\\left( L(\\theta) \\right)``.
- `method`: computational method to evaluate interval endpoint. Currently the following methods are implemented: `:CICO_ONE_PASS`, `:LIN_EXTRAPOL`, `:QUADR_EXTRAPOL`.
- `direction`: `:right` or `:left` endpoint to estimate.

## Keyword arguments
see [`get_interval`](@ref)

"""

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
        raise BaseException(f"theta_init is outside theta_bound: {np.where(theta_init_outside_theta_bounds)}")

    # scan_bound should be within theta_bounds
    if (not(theta_bounds[theta_num][0]) < scan_bound < theta_bounds[theta_num][1]):
        raise ValueError(f"scan_bound are outside of the theta_bounds {theta_bounds[theta_num]}")

    # theta_init should be within scan_bound
    if (theta_init[theta_num] >= scan_bound
        and not(isLeft)) or (theta_init[theta_num] <= scan_bound and isLeft):
        raise ValueError(f"init values are outside of the scan_bound {scan_bound}")

    # 0 <= theta_bound[1] for :log
    less_than_zero_theta_bounds = all(i == "log" for i in scale) \
                                  and [theta_bounds[i][0] < 0 for i in range(len(theta_init))]
    if less_than_zero_theta_bounds and any(less_than_zero_theta_bounds):
        raise ValueError(f":log scaled theta_bound min is negative: {np.where(less_than_zero_theta_bounds)}")

    # 0 <= theta_bounds <= 1 for :logit
    less_than_zero_theta_bounds = all(i == "logit" for i in scale) \
                                  and [theta_bounds[i][1] < 0 or theta_bounds[i][2] > 1 for i in range(len(theta_init))]
    if less_than_zero_theta_bounds and any(less_than_zero_theta_bounds):
        raise ValueError(f":logit scaled theta_bound min is outside range [0,1]: {np.where(less_than_zero_theta_bounds)}")


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