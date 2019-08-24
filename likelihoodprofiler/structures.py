class ProfilePoint:
    """
    Structure storing one point from profile function.
    """
    def __init__(self, value, loss, params, ret, counter):
        """

        :param value:
        :param loss:
        :param params:
        :param ret:
        :param counter:
        """
        self.value = value
        self.loss = loss
        self.params = params
        self.ret = ret
        self.counter = counter


class EndPoint:
    """
    Structure storing end point for confidence interval.
    """
    def __init__(self, value, profilePoints, status, direction, counter):
        """

        :param value:
        :param profilePoints:
        :param status:
        :param direction:
        :param counter:
        """
        self.value = value
        self.profilePoints = profilePoints
        self.status = status
        self.direction = direction
        self.counter = counter
