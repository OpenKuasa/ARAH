import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arah_icon_geom as geom  # noqa: E402


def area_centroid(poly):
    a = cx = cy = 0.0
    for i, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(i + 1) % len(poly)]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    a /= 2
    return cx / (6 * a), cy / (6 * a)


class IconGeomTest(unittest.TestCase):
    def test_arrow_centred_in_pin_head(self):
        p = geom._arrow_pts()
        cx, cy = area_centroid([p['tip'], p['wr'], p['notch'], p['wl']])
        self.assertAlmostEqual(cx, geom.CX, delta=1.0)
        self.assertAlmostEqual(cy, geom.HEAD_CY, delta=1.0)


if __name__ == '__main__':
    unittest.main()
