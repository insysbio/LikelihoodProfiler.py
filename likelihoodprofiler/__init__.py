import sys
import os

filename = os.path.join("../../")
sys.path.append(filename)
filename = os.path.join("../")
sys.path.append(filename)

from .get_endpoint import get_endpoint
from .get_interval import get_interval
from .cico_one_pass import get_right_endpoint_cico
from .get_right_endpoint_by_lin_extrapol import get_right_endpoint_by_lin_extrapol
from .method_quadr_extrapol import get_right_endpoint_by_quadr_extrapol
from .profile import profile