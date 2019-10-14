class ProfilePoint:
    """Structure storing one point from profile function.

    Parameters
    ----------
    value : Float64           # x value of profile point
    loss : Float64            # y value of profile point (loss function at value)
    params : Array[Float64]   # vector of optimal values of loss_func arguments
    ret : String              # return value from NLOpt.optimize()
    counter : Int             # number of loss_func() calls to calculate the value

    ret values - -5, 5, 3
    """
    def __init__(self, value, loss, params, ret, counter):
        self.value = value
        self.loss = loss
        self.params = params
        self.ret = ret
        self.counter = counter


class EndPoint:
    """Structure storing end point for confidence interval.

    Parameters
    ----------
    value : Float64 or None             # value of endpoint or nothing
    profilePoints : Array[ProfilePoint] # vector of profile points
    status : String                     # result of analysis
    direction : String                  # "right" or "left"
    counter : Int                       # number of loss_func() calls to calculate the endpoint
    supreme : Float64 or None           # maximal value inside profile interval

    status values - "BORDER_FOUND_BY_SCAN_TOL", "BORDER_FOUND_LOSS_TOL",
    "SCAN_BOUND_REACHED", "MAX_ITER_STOP", "LOSS_ERROR_STOP"

    """
    def __init__(self, value, profilePoints, status, direction, counter, supreme):
        self.value = value
        self.profilePoints = profilePoints
        self.status = status
        self.direction = direction
        self.counter = counter
        self.supreme = supreme
