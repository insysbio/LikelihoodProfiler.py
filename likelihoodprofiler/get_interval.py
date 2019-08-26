import nlopt
import numpy as np
import matplotlib.pyplot as plt

from .get_endpoint import get_endpoint, unscaling


class ParamIntervalInput:
    """Calculates right or left endpoint of CI for parameter component. It is a wripper
    of `get_right_endpoint` functions for selection of direction and using different
    transformations for faster optimization.

    Parameters
    ----------
    theta_init : Array[Float64]
        initial parameters vector
    theta_num : Int
        number of the parameter for analysis
    loss_func : Function
        loss function
    loss_crit : Float64
        loss function maximum value, "identifiability level
    scale : Array[String]
    theta_bounds : Array[[Float64, Float64]]
        search bounds for id parameter
    scan_bounds : Float64
    scan_tol : Float64
        fitting tolerance for local optimizer (default - 1e-3)
    loss_tol : Float64
        constraints tolerance
    local_alg : Function
        local fitting algorithm (default - LN_NELDERMEAD)
    fitter_options : Any

    """
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
    """Structure storing result of parameter interval calculation

    Parameters
    ----------
    input : ParamIntervalInput
    loss_init : Float64
    method : String
    result : Array[EndPoint, EndPoint]
    """
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
    """Computes confidence interval for single component `theta_num` of parameter vector
    and `loss_func` according to `loss_crit` level.

    Parameters
    ----------
    theta_init : Array[Float64]
        starting values of parameter vector :math:`\\Theta`. The starting values is not necessary to be the optimum values for `loss_func` but it the value of :code:`loss_func` must be lower than :code:`loss_crit`.
    theta_num : Int
        number `n` of vector component to compute confidence interval :math:`\\Theta^n`.
    loss_func : Function
        loss function :math:`\\Lambda\\left(\\theta\\right)` the profile of which is analyzed. Usually we use log-likelihood for profile analysis in form :math:`\\Lambda( \\theta ) = - 2 ln\\left( L(\\theta) \\right)`.
    method : String
        computational method to evaluate interval endpoint. Currently the following methods are implemented: :code:`CICO_ONE_PASS`, :code:`LIN_EXTRAPOL`, :code:`QUADR_EXTRAPOL`.
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
    ParamInterval
         structure storing all input data and estimated confidence interval.

    """

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
