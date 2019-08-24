import nlopt
import numpy as np
import matplotlib.pyplot as plt

from .get_endpoint import get_endpoint, unscaling


class ParamIntervalInput:
    def __init__(
        self,
        theta_init,
        theta_num,
        loss_func,
        loss_crit,
        scale,
        theta_bounds,
        scan_bounds,
        scan_tol,
        loss_tol,
        local_alg,
        fitter_options):
        self.theta_init = theta_init  # initial parameters vector
        self.theta_num = theta_num  # number of the parameter for analysis
        self.loss_func = loss_func  # loss function
        self.loss_crit = loss_crit  # loss function maximum value, "identifiability level"
        self.scale = scale
        self.theta_bounds = theta_bounds  # search bounds for id parameter
        self.scan_bounds = scan_bounds
        self.scan_tol = scan_tol  # fitting tolerance for local optimizer (default - 1e-3)
        self.loss_tol = loss_tol  # constraints tolerance
        self.local_alg = local_alg  # local fitting algorithm (default - :LN_NELDERMEAD)
        self.fitter_options = fitter_options


class ParamInterval:
    def __init__(self, input, loss_init, method, result):
        self.input = input
        self.loss_init = loss_init
        self.method = method
        self.result = result

    def plot(self):
        # input value
        loss_crit = self.input.loss_crit
        theta_num = self.input.theta_num
        init_point_x = self.input.theta_init[theta_num]
        loss_func = self.input.loss_func
        init_point = [init_point_x, loss_func(self.input.theta_init)]
        end_point_1 = self.result[0].value
        end_point_2 = self.result[1].value

        # calculate values
        values = map(lambda x: [x.value, x.loss],
                    self.result[0].profilePoints + self.result[1].profilePoints)
        values = list(values)
        values.sort()
        x_values, y_values = list(zip(*values))

        # plot critical level
        plt.axhline(y=loss_crit)

        # plot pp
        plt.plot(x_values, y_values, '.', linestyle='dashed', linewidth=2, markersize=12)

        # plot init point
        plt.plot(init_point[0], init_point[1], 'd')

        # plot verticle line
        if not(end_point_1 is None):
            plt.axvline(x=end_point_1)
        if not(end_point_2 is None):
            plt.axvline(x=end_point_2)

        plt.show()


def get_interval(
    theta_init,
    theta_num,
    loss_func,
    method,
    loss_crit=0.0,
    scale=[],
    theta_bounds=[],
    scan_bounds=None,
    scan_tol=1e-3,
    loss_tol=1e-3,
    local_alg=nlopt.LN_NELDERMEAD,
    **kwargs
    ):

    if len(scale) == 0:
        scale = np.tile("direct", len(theta_init))

    if len(theta_bounds) == 0:
        theta_bounds = unscaling(
            np.tile([(-1)*np.inf, np.inf], (len(theta_init), 1)),
            )

    if scan_bounds is None:
        scan_bounds = unscaling((-9.0, 9.0), scale[theta_num])

    # both endpoints
    endpoints = [get_endpoint(
        theta_init,
        theta_num,
        loss_func,
        method,
        ["left", "right"][i],
        loss_crit=loss_crit,
        scale=scale,
        theta_bounds=theta_bounds,
        scan_bound=scan_bounds[i],
        scan_tol=scan_tol,
        loss_tol=loss_tol,
        local_alg=local_alg,
        **kwargs
        ) for i in range(2)]

    input = ParamIntervalInput(
        theta_init,
        theta_num,
        loss_func,
        loss_crit,
        scale,
        theta_bounds,
        scan_bounds,
        scan_tol,
        loss_tol,
        local_alg,
        kwargs
        )

    return ParamInterval(
        input,
        loss_func(theta_init),
        method,
        endpoints
        )
