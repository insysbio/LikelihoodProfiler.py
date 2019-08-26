class ProfilePoint:
    """Structure storing one point from profile function.

    Parameters
    ----------
    value : Float64
    loss : Float64
    params : Array[Float64]
    ret : String
    counter : Int or
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
    value : Float64 or None
    profilePoints : Array[ProfilePoint]
    status : String
    direction : String
    counter : Int
    """
    def __init__(self, value, profilePoints, status, direction, counter):
        self.value = value
        self.profilePoints = profilePoints
        self.status = status
        self.direction = direction
        self.counter = counter
