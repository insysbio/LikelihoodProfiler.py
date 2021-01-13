from .. import get_endpoint
from .cases_func import f_3p_1im_dep
import math
import numpy as np
import unittest

method = "CICO_ONE_PASS"

class getEndpointTest(unittest.TestCase):
    def test_default_options(self):
        res0 = [get_endpoint(
            [3., 2., 2.1],
            i,
            lambda x: f_3p_1im_dep(x),
            method,
            loss_crit=9
        ) for i in range(3)]

        self.assertTrue(math.isclose(res0[0].value, 5.0, abs_tol=1e-2))
        self.assertTrue(len(res0[0].profilePoints) > 0)
        self.assertTrue(res0[0].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[0].direction == "right")

        self.assertTrue(math.isclose(res0[1].value, 2.0+2.0*math.sqrt(2.), abs_tol=1e-2))
        self.assertTrue(len(res0[1].profilePoints) > 0)
        self.assertTrue(res0[1].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[1].direction == "right")

        self.assertTrue(len(res0[2].profilePoints) == 0)
        self.assertTrue(res0[2].status == "SCAN_BOUND_REACHED")
        self.assertTrue(res0[2].direction == "right")

    def test_left_direction(self):
        res0 = [get_endpoint(
            [3., 2., 2.1],
            i,
            lambda x: f_3p_1im_dep(x),
            method,
            direction="left",
            loss_crit=9
        ) for i in range(3)]

        self.assertTrue(math.isclose(res0[0].value, 1.0, abs_tol=1e-2))
        self.assertTrue(len(res0[0].profilePoints) > 0)
        self.assertTrue(res0[0].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[0].direction == "left")

        self.assertTrue(math.isclose(res0[1].value, 2.0 - 2.0 * math.sqrt(2.), abs_tol=1e-2))
        self.assertTrue(len(res0[1].profilePoints) > 0)
        self.assertTrue(res0[1].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[1].direction == "left")

        self.assertTrue(len(res0[2].profilePoints) == 0)
        self.assertTrue(res0[2].status == "SCAN_BOUND_REACHED")
        self.assertTrue(res0[2].direction == "left")

    def test_log(self):
        res0 = [get_endpoint(
                [3., 2., 2.1],
                i,
                lambda x: f_3p_1im_dep(x),
                method,
                loss_crit=9,
                scale=["log","direct", "log"]
        ) for i in range(3)]

        self.assertTrue(math.isclose(np.log10(res0[0].value), np.log10(5.), abs_tol=1e-2))
        self.assertTrue(len(res0[0].profilePoints) > 0)
        self.assertTrue(res0[0].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[0].direction == "right")

        self.assertTrue(math.isclose(res0[1].value, 2.0 + 2.0 * math.sqrt(2.), abs_tol=1e-2))
        self.assertTrue(len(res0[1].profilePoints) > 0)
        self.assertTrue(res0[1].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[1].direction == "right")

        self.assertTrue(len(res0[2].profilePoints) == 0)
        self.assertTrue(res0[2].status == "SCAN_BOUND_REACHED")
        self.assertTrue(res0[2].direction == "right")
#unittest.main(argv=['first-arg-is-ignored'], exit=False)
