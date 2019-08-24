from .. import get_interval
from .cases_func import f_3p_1im_dep
import math
import unittest

class getEndpointTest(unittest.TestCase):
    def test_default(self):
        res0 = [get_interval(
            [3., 2., 2.1],
            i,
            lambda x: f_3p_1im_dep(x),
            "CICO_ONE_PASS",
            loss_crit=9
        ) for i in range(3)]

        self.assertTrue(math.isclose(res0[0].result[0].value, 1.0, abs_tol=1e-2))
        self.assertTrue(math.isclose(res0[0].result[1].value, 5.0, abs_tol=1e-2))
        self.assertTrue(len(res0[0].result[0].profilePoints) > 0)
        self.assertTrue(len(res0[0].result[1].profilePoints) > 0)
        self.assertTrue(res0[0].result[0].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[0].result[1].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[0].result[0].direction == "left")
        self.assertTrue(res0[0].result[1].direction == "right")

        self.assertTrue(math.isclose(res0[1].result[0].value, 2.0-2.0*math.sqrt(2), abs_tol=1e-2))
        self.assertTrue(math.isclose(res0[1].result[1].value, 2.0+2.0*math.sqrt(2), abs_tol=1e-2))
        self.assertTrue(res0[1].result[0].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[1].result[1].status == "BORDER_FOUND_BY_SCAN_TOL")
        self.assertTrue(res0[2].result[0].status == "SCAN_BOUND_REACHED")
        self.assertTrue(res0[2].result[1].status == "SCAN_BOUND_REACHED")


#unittest.main(argv=['first-arg-is-ignored'], exit=False)
