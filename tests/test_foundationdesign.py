import unittest
from FoundationDesign.foundationdesign import padFoundationDesign, PadFoundation


class PadFoundationDesignTestCase(unittest.TestCase):
    def setUp(self):
        fdn = PadFoundation(
            foundation_length=3600,
            foundation_width=3000,
            column_length=450,
            column_width=450,
            col_pos_xdir=1800,
            col_pos_ydir=1500,
            soil_bearing_capacity=150,
        )

        z = fdn.foundation_loads(
            foundation_thickness=550,
            soil_depth_abv_foundation=0,
            soil_unit_weight=18,
            concrete_unit_weight=24,
        )

        fdn.column_axial_loads(permanent_axial_load=770, imposed_axial_load=330)
        fdn.column_horizontal_loads_xdir(
            permanent_horizontal_load_xdir=35, imposed_horizontal_load_xdir=15
        )
        fdn.column_moments_xdir(permanent_moment_xdir=78, imposed_moment_xdir=34)
        self.pad_foundation = fdn

    def test_foundation_loads(self):
        pad_foundation = self.pad_foundation
        self.assertEqual(
            pad_foundation.foundation_loads(
                foundation_thickness=550,
                soil_depth_abv_foundation=0,
                soil_unit_weight=18,
                concrete_unit_weight=24,
            ),
            [13.2, 0.0],
        )

    def test_minimum_area_of_foundation(self):
        pad_foundation = self.pad_foundation
        self.assertEqual(pad_foundation.minimum_area_required(), 10.24)

    def test_total_loads_moments(self):
        pad_foundation = self.pad_foundation
        self.assertEqual(pad_foundation.total_force_X_dir_sls(), 50)
        self.assertEqual(pad_foundation.total_force_Y_dir_sls(), 0)
        self.assertEqual(pad_foundation.total_force_Z_dir_sls(), 1242.56)
        self.assertEqual(pad_foundation.total_force_X_dir_uls(), 69.75)
        self.assertEqual(pad_foundation.total_force_Y_dir_uls(), 0)
        self.assertEqual(pad_foundation.total_moments_X_direction_sls(), 2376.108)
        self.assertEqual(pad_foundation.total_moments_Y_direction_sls(), 1863.84)
        self.assertEqual(pad_foundation.total_moments_X_direction_uls(), 3303.183)
        self.assertEqual(pad_foundation.total_moments_Y_direction_uls(), 2590.434)

    def test_eccentricities(self):
        pad_foundation = self.pad_foundation
        self.assertEqual(pad_foundation.eccentricity_X_direction_uls(), 112.72)
        self.assertEqual(pad_foundation.eccentricity_Y_direction_uls(), 0)
        self.assertEqual(pad_foundation.eccentricity_X_direction_sls(), 112)
        self.assertEqual(pad_foundation.eccentricity_Y_direction_sls(), 0)

    def test_pad_base_pressure(self):
        pad_foundation = self.pad_foundation
        self.assertTupleEqual(
            pad_foundation.pad_base_pressures_sls(), (93.576, 93.576, 136.528, 136.528)
        )
        self.assertTupleEqual(
            pad_foundation.pad_base_pressures_uls(),
            (129.863, 129.863, 189.944, 189.944),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
