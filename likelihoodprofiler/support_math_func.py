import math

import numpy as np

"""
    logit10(x)
Function transforming interval [0,1] to [-Inf, Inf] using logit transformation.
"""


def logit10(x):
    return math.log(x / (1.0 - x), 10)

"""
    logistic10(x::Float64)
Function transforming interval [-Inf, Inf] to [0,1] using logistic transformation.
Inverse function for [`logit10`](@ref).
"""


def logistic10(x):
    10**(x) / (10**(x) + 1.0)


"""
    scaling(x::Float64, scale::Symbol = :direct)
Transforms values from specific scale to range [-Inf, Inf] based on option.

## Return
Transformed value.

## Arguments
* `x`: input value.
* `scale`: transformation type: `:direct, :log, :logit`.
"""


def scaling(x, scale="direct"):
    if x == np.inf * (-1):
        return np.inf * (-1)

    if scale == "direct":
        return x
    elif scale == "log":
        return np.log10(x)
    elif scale == "logit":
        return np.logit10(x)
    else:
        raise ValueError(scale, "scale type is not supported")

"""
    unscaling(x::Float64, scale::Symbol = :direct)
Transforms values from [-Inf, Inf] to specific scale based on option. Inverse function
for [`scaling`](@ref).

## Return
Transformed value.

## Arguments
* `x`: input value.
* `scale`: transformation type: `:direct, :log, :logit`.
"""


def unscaling(x, scale="direct"):
    """
    print("---UNSCALING---")
    print(x)
    print(scale)
    print("---UNSCALING---")
    """
    if x is None:
        return None
    if scale == "direct":
        return x
    elif scale == "log":
        return np.power(10, x)
    elif scale == "logit":
        return logistic10(x)
    else:
        raise BaseException("scale type is not supported") #DomainError
