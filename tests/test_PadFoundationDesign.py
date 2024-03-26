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
        fdn_design = padFoundationDesign(
            fdn, fck=30, fyk=500, concrete_cover=30, bar_diameterX=16, bar_diameterY=16
        )
        self.pad_foundation_design = fdn_design

    def test_foundation_plots(self):
        pad_foundation_design = self.pad_foundation_design
        # check plotting valid
        # pad_foundation_design.plot_foundation_loading_X()
        # pad_foundation_design.plot_foundation_loading_Y()
        # pad_foundation_design.plot_bending_moment_X()
        # pad_foundation_design.plot_bending_moment_Y()
        # pad_foundation_design.plot_shear_force_Y()
        self.assertEqual(pad_foundation_design.get_design_moment_X(), 607.861)
        self.assertEqual(pad_foundation_design.get_design_moment_Y(), 415.754)
        self.assertEqual(pad_foundation_design.get_design_shear_force_X(), 520.616)
        self.assertEqual(pad_foundation_design.get_design_shear_force_Y(), 398.459)

    def test_reinforcement_calculations(self):
        pad_foundation_design = self.pad_foundation_design
        self.assertEqual(pad_foundation_design.area_of_steel_reqd_X_dir(), 958)
        self.assertEqual(pad_foundation_design.area_of_steel_reqd_Y_dir(), 747)
        self.assertDictEqual(
            pad_foundation_design.reinforcement_provision_flexure_X_dir(),
            {
                "steel_label": "H",
                "bar_diameter": "16mm",
                "bar_spacing": 200.0,
                "area_provided": 1005,
                "status": "Provide H16mm bars spaced at 200.0mm c/c bottom. The area provided is 1005mm²/m parallel to the 3.6m side",
            },
        )
        self.assertDictEqual(
            pad_foundation_design.reinforcement_provision_flexure_Y_dir(),
            {
                "steel_label": "H",
                "bar_diameter": "12mm",
                "bar_spacing": 150.0,
                "area_provided": 754,
                "status": "Provide H12mm bars spaced at 150.0mm c/c bottom. The area provided is 754mm²/m parallel to the 3.6m side",
            },
        )

    def test_punching_shear(self):
        pad_foundation_design = self.pad_foundation_design
        self.assertDictEqual(
            pad_foundation_design.punching_shear_column_face(),
            {
                "design_punching_shear_stress": 1.691468253968254,
                "maximum_punching_shear_resistance": 4.488,
                "status": "The maximum punching shear resistance of 4.488N/mm² exceeds the design punching shear stress of 1.691N/mm² - PASS!!!",
            },
        )
        self.assertDictEqual(
            pad_foundation_design.punching_shear_check_1d(),
            {
                "punching_shear_stress": 0.798,
                "ved_design": 0.5876415001228639,
                "status": "The maximum punching shear resistance of 0.798N/mm² exceeds the design punching shear stress of 0.588N/mm² - PASS!!!",
            },
        )
        self.assertDictEqual(
            pad_foundation_design.punching_shear_check_2d(),
            {
                "design_punching_shear_stress": 0.22247511396970102,
                "shear_resistance_max": 0.399,
                "status": "The maximum punching shear resistance of 0.399N/mm² exceeds the design punching shear stress of 0.222N/mm² - PASS!!!",
            },
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
