# Standard library imports
import math

# Third Party Imports
import numpy as np
import plotly.graph_objs as go
from indeterminatebeam import Beam, Support, TrapezoidalLoadV, DistributedLoadV

# Local Application Imports
from FoundationDesign.datavalidation import (
    assert_input_limit,
    assert_number,
    assert_strictly_positive_number,
    assert_maximum_input_limit,
    assert_input_range,
)
from FoundationDesign.concretedesignfunc import (
    bending_reinforcement,
    minimum_steel,
    shear_stress_check_1d,
    column_punching_coefficient_k,
    reinforcement_provision,
)


class PadFoundation:
    """
    Represents a rectangular or square pad foundation that can take permanent,variable and wind loads.

    This class serves as the main class that helps analyse the foundation to get the forces needed to design the 
    foundation against.

    Attributes
    ----------
    uls_strength_factor_permanent : int or float, default 1.35
        Strength factor that is used to estimate permanent loads at ultimate limit state. This value is according to
        the STR combination. In this code, the equation to estimate uls loads has been taken according to (Exp. (6.10)) of
        the Eurocode 1. To access better economy in design,this attribute can be changed and set according to
        equations (6.10a) or (6.10b) from the Eurocode.
    uls_strength_factor_imposed : int or float, default 1.5
        Strength factor that is used to estimate imposed loads at ultimate limit state. This value is according to
        the STR combination. In this code, the equation to estimate uls loads has been taken according to (Exp. (6.10)) of
        the Eurocode 1.To access better economy in design,this attribute can be changed and set according to
        equations (6.10a) or (6.10b) from the Eurocode.
    uls_strength_factor_imposed_unfavourable : int or float, default 0
        Strength factor that is used to estimate unfavourable imposed loads at ultimate limit state for example wind loads.
        This value is according to the STR combination. In this code, the equation to estimate uls loads has been
        taken according to (Exp. (6.10)) of the Eurocode 1.To access better economy in design, this attribute can be
        changed and set according to equations (6.10a) or (6.10b) from the Eurocode.

    Methods
    -------
    area_of_foundation()
        Calculates the area of the foundation.
    plot_geometry()
        Plots the geometry of the foundation, showing the column position relative to the pad base.
    foundation_loads(foundation_thickness=300, soil_depth_abv_foundation=700, soil_unit_weight=18, concrete_unit_weight=24)
        Calculates the total load on the foundation due to surcharge loads and self weight of the pad base itself.
    column_axial_loads(permanent_axial_load=0, imposed_axial_load=0, wind_axial_load=0)
        Accepts the columnn axial loads the foundation is being subjected to.Inform of permanent,imposed and wind axial loads.
    column_horizontal_loads_xdir(permanent_horizontal_load_xdir=0, imposed_horizontal_load_xdir=0, wind_horizontal_load_xdir=0)
        Accepts the column horizontal loads along the X direction. This comprises of permanent,imposed and wind horizontal loads.
    column_horizontal_loads_ydir(permanent_horizontal_load_ydir=0, imposed_horizontal_load_ydir=0, wind_horizontal_load_ydir=0)
        Accepts the column horizontal loads along the Y direction. This comprises of permanent,imposed and wind horizontal loads.
    column_moments_xdir(permanent_moment_xdir=0, imposed_moment_xdir=0, wind_moments_xdir=0):
        Accepts the column moments along the X direction. This comprises of permanent,imposed and wind moments
    column_moments_ydir(permanent_moment_ydir=0, imposed_moment_ydir=0, wind_moments_ydir=0):
        Accepts the column moments along the X direction. This comprises of permanent,imposed and wind moments
    total_force_X_dir_sls()
        Calculates the total force on the foundation in the x direction using the serviceability limit state combination.
    total_force_Y_dir_sls()
        Calculates the total force on the foundation in the y direction using the serviceability limit state combination.
    total_force_Z_dir_sls()
        Calculates the total force on the foundation in the z direction using the serviceability limit state combination.
    total_moments_X_direction_sls()
        Calculates the total moments on the foundation in the X direction using the serviceability limit state combination.
    total_moments_Y_direction_sls()
        Calculates the total moments on the foundation in the Y direction using the serviceability limit state combination.
    eccentricity_X_direction_sls()
        Calculates the foundation eccentricity in the X direction using the serviceability limit state combination.
    eccentricity_Y_direction_sls()
        Calculates the foundation eccentricity in the Y direction using the serviceability limit state combination.
    pad_base_pressures_sls()
        Calculates the pad foundation pressures at the four corners of the foundation using the serviceability limit state
        combination.
    bearing_pressure_check_sls()
        Checks that calculated foundation pressure does not exceed the allowable bearing pressure supplied at serviceability
        limit state.
    plot_base_pressures_sls()
        Plots the foundation pressures at each corners of the foundation using the serviceability limit state combination.
    total_force_X_dir_uls()
        Calculates the total force on the foundation in the x direction using the ultimate limit state combination.
    total_force_Y_dir_uls()
        Calculates the total force on the foundation in the y direction using the ultimate limit state combination.
    total_force_Z_dir_uls()
        Calculates the total force on the foundation in the z direction using the ultimate limit state combination.
    total_moments_X_direction_uls()
        Calculates the total moments on the foundation in the X direction using the ultimate limit state combination.
    total_moments_Y_direction_uls()
        Calculates the total moments on the foundation in the Y direction using the ultimate limit state combination.
    eccentricity_X_direction_uls()
        Calculates the foundation eccentricity in the X direction using the ultimate limit state combination.
    eccentricity_Y_direction_uls()
        Calculates the foundation eccentricity in the Y direction using the ultimate limit state combination.
    pad_base_pressures_uls()
        Calculates the pad foundation pressures at the four corners of the foundation using the ultimate limit state
        combination.
    base_pressure_rate_of_change_X()
        Calculates the rate of change of the base pressure at each meter of the foundation length using Ultimate Limit State
        combination.
    base_pressure_rate_of_change_Y()
        Calculates the rate of change of the base pressure at each meter of the foundation width using Ultimate Limit State
        combination.
    """

    uls_strength_factor_permanent = 1.35
    uls_strength_factor_imposed = 1.5
    uls_strength_factor_imposed_unfavourable = 0

    def __init__(
        self,
        foundation_length: float,
        foundation_width: float,
        column_length: float,
        column_width: float,
        col_pos_xdir: float,
        col_pos_ydir: float,
        soil_bearing_capacity=150,
    ):
        """

        Initializes a pad foundation object.

        Parameters
        ----------
        foundation_length : float
            Length of the foundation. The length of the foundation is along the x axis (default unit mm). Must be positive
            and should not be less than 800mm
        foundation_width : float
            Width of the foundation. The width of the foundation is along the y axis (default unit mm). Must be positive
            and should not be less than 800mm
        column_length : float
            Length of the column. The length of the column is along the x axis (default unit mm). Must be positive
            and should not be less than 100mm
        column_width : float
            Width of the column. The width of the column is along the y axis (default unit mm). Must be positive
            and should not be less than 100mm
        col_pos_xdir : float
            The position of the column along the length of the foundation in the x axis. This is used to model eccentric foundations
            i.e a situation where the column is not placed centrally on the foundation. If the column is at the centre of the
            foundation then this value should be equal to the foundation length divided by two. Else the distance should be specified.
            (default unit mm). This value should not be greater than the foundation length.
        col_pos_ydir : float
            The position of the column along the width of the foundation in the y axis. This is used to model eccentric foundations
            i.e a situation where the column is not placed centrally on the foundation. If the column is at the centre of the
            foundation then this value should be equal to the foundation width divided by two. Else the distance should be specified.
            (default unit mm). This value should not be greater than the foundation width.
        soil_bearing_capacity : float, default 150
            Represents the presumed bearing capacity of the foundation.(default unit kN/m2) The assumption here is
            that previous geotechnical calculations must have been done to ascertain the soil bearing capacity. This tool
            cannot analyse the bearing capacity in accordance to Eurocode 7. That can be easily done on civils.ai website and
            thereafter the values of presumed bearing capacuty can be inputed in here.
        """
        # data validation for inputs
        assert_strictly_positive_number(foundation_length, "foundation_length")
        assert_strictly_positive_number(foundation_width, "foundation_width")
        assert_strictly_positive_number(column_length, "column_length")
        assert_strictly_positive_number(column_width, "column_width")
        assert_strictly_positive_number(col_pos_xdir, "col_pos_xdir")
        assert_strictly_positive_number(col_pos_ydir, "col_pos_ydir")
        assert_strictly_positive_number(soil_bearing_capacity, "soil_bearing_capacity")
        # data validation for inputs
        assert_input_limit(foundation_length, 800, "foundation length")
        assert_input_limit(foundation_width, 800, "foundation width")
        assert_input_limit(column_length, 100, "column length")
        assert_input_limit(column_width, 100, "column width")
        assert_maximum_input_limit(
            col_pos_xdir, foundation_length, "column position x direction"
        )
        assert_maximum_input_limit(
            col_pos_ydir, foundation_width, "column position y direction"
        )

        self.foundation_length = foundation_length / 1000
        self.foundation_width = foundation_width / 1000
        self.column_length = column_length / 1000
        self.column_width = column_width / 1000
        self.soil_bearing_capacity = soil_bearing_capacity
        self.foundation_thickness = 0
        self.soil_depth_abv_foundation = 0
        self.soil_unit_weight = 18
        self.concrete_unit_weight = 24
        self.permanent_axial_load = 0
        self.permanent_horizontal_load_xdir = 0
        self.permanent_horizontal_load_ydir = 0
        self.permanent_moment_xdir = 0
        self.permanent_moment_ydir = 0
        self.imposed_axial_load = 0
        self.imposed_horizontal_load_xdir = 0
        self.imposed_horizontal_load_ydir = 0
        self.imposed_moment_xdir = 0
        self.imposed_moment_ydir = 0
        self.wind_axial_load = 0
        self.wind_horizontal_load_xdir = 0
        self.wind_horizontal_load_ydir = 0
        self.wind_moments_xdir = 0
        self.wind_moments_ydir = 0
        self.col_pos_xdir = col_pos_xdir / 1000
        self.col_pos_ydir = col_pos_ydir / 1000

    def area_of_foundation(self):
        """
        Calculates the area of the foundation.

        Returns
        -------
        float
            The area of the foundation in m^2.
        """
        return self.foundation_length * self.foundation_width

    def plot_geometry(self):
        """Plots the geometry of the foundation, showing the column position relative to the pad base"""
        fig_plan = go.Figure()
        y = [0, 0, self.foundation_width, self.foundation_width, 0]
        x = [0, self.foundation_length, self.foundation_length, 0, 0]

        x_col = [
            self.col_pos_xdir - self.column_length / 2,
            self.col_pos_xdir + self.column_length / 2,
            self.col_pos_xdir + self.column_length / 2,
            self.col_pos_xdir - self.column_length / 2,
            self.col_pos_xdir - self.column_length / 2,
        ]
        y_col = [
            self.col_pos_ydir - self.column_width / 2,
            self.col_pos_ydir - self.column_width / 2,
            self.col_pos_ydir + self.column_width / 2,
            self.col_pos_ydir + self.column_width / 2,
            self.col_pos_ydir - self.column_width / 2,
        ]
        fig_plan.add_trace(
            go.Scatter(
                x=x, y=y, name="FOOTING", mode="lines", line=dict(color="red", width=3)
            )
        )
        fig_plan.add_trace(
            go.Scatter(
                x=x_col,
                y=y_col,
                name="COLUMN",
                mode="lines",
                line=dict(color="green", width=1.5),
            )
        )

        fig_plan.update_layout(
            title_text="FOOTING PLAN", width=500, height=500, showlegend=True
        )
        fig_plan.show()

    def foundation_loads(
        self,
        foundation_thickness=300,
        soil_depth_abv_foundation=500,
        soil_unit_weight=18,
        concrete_unit_weight=24,
    ):
        """
        Calculates the foundation self weight which includes the soil weight above the foundation in order terms surchage
        loads and also the self weight of the concrete base

        Parameters
        ----------
        foundation_thickness : float
            Represents the depth of the foundation. (default unit mm). The default value is 300mm
        soil_depth_abv_foundation : float, default 500
            Represents the depth of soil above the foundation is added to the self weight of the footing to arrive at the
            foundation own loads.(default unit mm). The default value is 500mm, If this value should not be included in the
            calculations, then this parameter should be explicitly set to zero
        soil_unit_weight_soil : float, default 18
            The default unit weight of the soil is 18kN/mm^3. (default unit kN/mm^3).
        concrete_unit_weight : float, default 24
            The default unit weight of the concrete is 24kN/mm^3 (default unit kN/mm^3).

        Returns
        -------
        list
            self weight : float
            soil weight : float
        """
        assert_number(foundation_thickness, "foundation_thickness")
        assert_number(soil_depth_abv_foundation, "soil_depth_abv_foundation")
        assert_number(soil_unit_weight, "soil_unit_weight")
        assert_number(concrete_unit_weight, "concrete_unit_weight")

        self.foundation_thickness = foundation_thickness / 1000
        self.soil_depth_abv_foundation = soil_depth_abv_foundation / 1000
        self.soil_unit_weight = soil_unit_weight
        self.concrete_unit_weight = concrete_unit_weight

        # data validation for inputs
        assert_input_limit(
            foundation_thickness,
            self.foundation_thickness * 1000,
            "Pad foundation thickness",
        )
        assert_input_limit(
            soil_depth_abv_foundation,
            self.soil_depth_abv_foundation * 1000,
            "Soil Depth Above Foundation",
        )
        assert_input_limit(soil_unit_weight, 18, "Soil Unit Weight")
        assert_input_limit(concrete_unit_weight, 24, "Concrete Unit Weight")

        foundation_self_weight = self.foundation_thickness * self.concrete_unit_weight
        soil_weight = self.soil_depth_abv_foundation * self.soil_unit_weight
        x = round(foundation_self_weight, 3), round(soil_weight, 3)
        return list(x)

    def column_axial_loads(
        self, permanent_axial_load=0, imposed_axial_load=0, wind_axial_load=0
    ):
        """
        Accepts the columnn axial loads the foundation is being subjected to.Inform of permanent,imposed
        and wind axial loads.

        Parameters
        ---------
        permanent_axial_load : float, default 0
            Represents the permanent axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN).
        imposed_axial_load : float, default 0
            Represents the imposed axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN).
        wind_axial_load : float, default 0
            Represents the wind axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN).
        """
        self.permanent_axial_load = permanent_axial_load
        self.imposed_axial_load = imposed_axial_load
        self.wind_axial_load = wind_axial_load
        # data validation for inputs
        assert_number(permanent_axial_load, "Permanent Axial Loads")
        assert_number(imposed_axial_load, "Imposed Axial Loads")
        assert_number(wind_axial_load, "Wind Axial Loads")

    def column_horizontal_loads_xdir(
        self,
        permanent_horizontal_load_xdir=0,
        imposed_horizontal_load_xdir=0,
        wind_horizontal_load_xdir=0,
    ):
        """
        Accepts the column horizontal loads along the X direction. This comprises of permanent,
        imposed and wind horizontal loads.

        Parameters
        ---------
        permanent_horizontal_load_xdir : float, default 0
            Represents permanent horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left. (default unit = kN)
        imposed_horizontal_load_xdir : float, default 0
            Represents imposed horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left. (default unit = kN)
        wind_horizontal_load_xdir : float, default 0
            Represents wind horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left. (default unit = kN)
        """

        self.permanent_horizontal_load_xdir = permanent_horizontal_load_xdir
        self.imposed_horizontal_load_xdir = imposed_horizontal_load_xdir
        self.wind_horizontal_load_xdir = wind_horizontal_load_xdir
        # data validation for inputs
        assert_number(
            permanent_horizontal_load_xdir, "Permanent Horizontal loads in X direction"
        )
        assert_number(
            imposed_horizontal_load_xdir, "Imposed Horizontal loads in X direction"
        )
        assert_number(wind_horizontal_load_xdir, "Wind Horizontal loads in X direction")

    def column_horizontal_loads_ydir(
        self,
        permanent_horizontal_load_ydir=0,
        imposed_horizontal_load_ydir=0,
        wind_horizontal_load_ydir=0,
    ):
        """
        Accepts the column horizontal loads along the Y direction. This comprises of permanent,
        imposed and wind horizontal loads.

        Parameters
        ---------
        permanent_horizontal_load_ydir : float, default 0
            Represents permanent horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom. (default unit = kN)
        imposed_horizontal_load_ydir : float, default 0
            Represents imposed horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom. (default unit = kN)
        wind_horizontal_load_ydir : float, default 0
            Represents wind horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom. (default unit = kN)
        """
        self.permanent_horizontal_load_ydir = permanent_horizontal_load_ydir
        self.imposed_horizontal_load_ydir = imposed_horizontal_load_ydir
        self.wind_horizontal_load_ydir = wind_horizontal_load_ydir
        # data validation for inputs
        assert_number(
            permanent_horizontal_load_ydir, "Permanent Horizontal loads in Y direction"
        )
        assert_number(
            imposed_horizontal_load_ydir, "Imposed Horizontal loads in Y direction"
        )
        assert_number(wind_horizontal_load_ydir, "Wind Horizontal loads in Y direction")

    def column_moments_xdir(
        self, permanent_moment_xdir=0, imposed_moment_xdir=0, wind_moments_xdir=0
    ):
        """
        Accepts the column moments along the X direction. This comprises of permanent,imposed and wind moments

        Parameters
        ----------
        permanent_moment_xdir : float, default 0
            Represents permanent moments in the x direction acting about the y axis. Positive moments act from
            left to right while negative moments acts from right to left (default unit = kNm).
        imposed_moment_xdir : float, default 0
            Represents imposed moments in the x direction acting about the y axis. Positive moments act from
            left to right while negative moments acts from right to left (default unit = kNm).
        wind_moment_xdir : float, default 0
            Represents wind moments in the x direction acting about the y axis. Positive moments act from
            left to right while negative moments acts from right to left (default unit = kNm).
        """
        self.permanent_moment_xdir = permanent_moment_xdir
        self.imposed_moment_xdir = imposed_moment_xdir
        self.wind_moments_xdir = wind_moments_xdir
        # data validation for inputs
        assert_number(permanent_moment_xdir, "Permanent moments in X direction")
        assert_number(imposed_moment_xdir, "Imposed moments in X direction")
        assert_number(wind_moments_xdir, "Wind moments in X direction")

    def column_moments_ydir(
        self, permanent_moment_ydir=0, imposed_moment_ydir=0, wind_moments_ydir=0
    ):
        """
        Accepts the column moments along the Y direction. This comprises of permanent,imposed and wind moments

        Parameters
        ----------
        permanent_moment_xdir : float, default 0
            Represents permanent moments in the y axis direction acting about the x axis. Positive moments act from
            bottom to top while negative moments acts from top to bottom (default unit = kNm).
        imposed_moment_xdir : float, default 0
            Represents imposed moments in the y direction acting about the x axis. Positive moments act from
            bottom to top while negative moments acts from top to bottom (default unit = kNm).
        wind_moment_xdir : float, default 0
            Represents wind moments in the y direction acting about the x axis. Positive moments act from
            bottom to top while negative moments acts from top to bottom (default unit = kNm).
        """
        self.permanent_moment_ydir = permanent_moment_ydir
        self.imposed_moment_ydir = imposed_moment_ydir
        self.wind_moments_ydir = wind_moments_ydir

        # data validation for inputs
        assert_number(permanent_moment_ydir, "Permanent moments in Y direction")
        assert_number(imposed_moment_ydir, "Imposed moments in Y direction")
        assert_number(wind_moments_ydir, "Wind moments in Y direction")

    def total_force_X_dir_sls(self):
        """
        Calculates the total force on the foundation in the x direction using the serviceability limit state combination
        of 1.0gk + 1.0qk + 1.0wk

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in x direction in kN
        """
        return (
            self.permanent_horizontal_load_xdir
            + self.imposed_horizontal_load_xdir
            + self.wind_horizontal_load_xdir
        )

    def total_force_Y_dir_sls(self):
        """
        Calculates the total force on the foundation in the y direction using the serviceability limit state combination
        of 1.0gk + 1.0qk + 1.0wk

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in y direction in kN
        """
        return (
            self.permanent_horizontal_load_ydir
            + self.imposed_horizontal_load_ydir
            + self.wind_horizontal_load_ydir
        )

    def total_force_Z_dir_sls(self):
        """
        Calculates the total axial force at serviceability limit states of 1.0gk + 1.0qk + 1.0wk.
        The foundation loads are converted to kN and added to the total axial loads from permanent,imposed and wind loads.

        Returns
        -------
        float
            sum of permanent,imposed and wind axial loads including foundation loads in kN
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )
        return (
            self.permanent_axial_load
            + self.imposed_axial_load
            + self.wind_axial_load
            + (self.area_of_foundation() * (fdn_loads[0] + fdn_loads[1]))
        )

    def total_moments_X_direction_sls(self):
        """
        Calculates the total moments on the foundation in the X direction using the serviceability limit state combination.

        Returns
        -------
        float
            total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )
        Mdx = (
            (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * (self.foundation_length / 2)
            )
            + (self.permanent_axial_load * self.col_pos_xdir)
            + self.permanent_moment_xdir
            + (self.permanent_horizontal_load_xdir * self.foundation_thickness)
            + (self.imposed_axial_load * self.col_pos_xdir)
            + self.imposed_moment_xdir
            + (self.imposed_horizontal_load_xdir * self.foundation_thickness)
            + (self.wind_axial_load * self.col_pos_xdir)
            + self.wind_moments_xdir
            + (self.wind_horizontal_load_xdir * self.foundation_thickness)
        )
        return round(Mdx, 3)

    def total_moments_Y_direction_sls(self):
        """
        Calculates the total moments on the foundation in the Y direction using the serviceability limit state combination.

        Returns
        -------
        float
            total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )
        Mdy = (
            self.area_of_foundation()
            * (fdn_loads[0] + fdn_loads[1])
            * self.foundation_width
            / 2
            + self.permanent_axial_load * self.col_pos_ydir
            + self.permanent_moment_ydir
            + self.permanent_horizontal_load_ydir * self.foundation_thickness
            + self.imposed_axial_load * self.col_pos_ydir
            + self.imposed_moment_ydir
            + self.imposed_horizontal_load_ydir * self.foundation_thickness
            + self.wind_axial_load * self.col_pos_ydir
            + self.wind_moments_ydir
            + self.wind_horizontal_load_ydir * self.foundation_thickness
        )
        return round(Mdy, 3)

    def eccentricity_X_direction_sls(self):
        """
        Calculates the foundation eccentricity in the X direction using the serviceability limit state combination.

        Returns
        -------
        float
            the eccentricity of the foundation in x direction units are in mm.
        """
        ex = (self.total_moments_X_direction_sls() / self.total_force_Z_dir_sls()) - (
            self.foundation_length / 2
        )
        return round(1000 * ex)

    def eccentricity_Y_direction_sls(self):
        """
        Calculates the foundation eccentricity in the Y direction using the serviceability limit state combination.

        Returns
        -------
        float
            the eccentricity of the foundation in y direction units are in mm.
        """
        ey = (self.total_moments_Y_direction_sls() / self.total_force_Z_dir_sls()) - (
            self.foundation_width / 2
        )
        return round(1000 * ey)

    def minimum_area_required(self):
        """
        Calculates the minimum area of base required.

        Returns
        -------
        float
            Minimum Area required in m2.
        """

        for x, y in zip(np.arange(1, 20.5, 0.05), np.arange(1, 20.5, 0.05)):
            x = np.round(x, 3)
            y = np.round(y, 3)
            fdn_loads = self.foundation_loads(
                self.foundation_thickness * 1000,
                self.soil_depth_abv_foundation * 1000,
                self.soil_unit_weight,
                self.concrete_unit_weight,
            )
            total_force_Z_direction = (
                self.permanent_axial_load
                + self.imposed_axial_load
                + self.wind_axial_load
                + ((x * x) * (fdn_loads[0] + fdn_loads[1]))
            )
            Mdx = (
                (x * y * (fdn_loads[0] + fdn_loads[1]) * (x / 2))
                + (self.permanent_axial_load * x / 2)
                + self.permanent_moment_xdir
                + (self.permanent_horizontal_load_xdir * self.foundation_thickness)
                + (self.imposed_axial_load * x / 2)
                + self.imposed_moment_xdir
                + (self.imposed_horizontal_load_xdir * self.foundation_thickness)
                + (self.wind_axial_load * x / 2)
                + self.wind_moments_xdir
                + (self.wind_horizontal_load_xdir * self.foundation_thickness)
            )
            Mdy = (
                (x * y * (fdn_loads[0] + fdn_loads[1]) * y / 2)
                + self.permanent_axial_load * y / 2
                + self.permanent_moment_ydir
                + self.permanent_horizontal_load_ydir * self.foundation_thickness
                + self.imposed_axial_load * y / 2
                + self.imposed_moment_ydir
                + self.imposed_horizontal_load_ydir * self.foundation_thickness
                + self.wind_axial_load * y / 2
                + self.wind_moments_ydir
                + self.wind_horizontal_load_ydir * self.foundation_thickness
            )
            ex = Mdx / total_force_Z_direction - x / 2
            ey = Mdy / total_force_Z_direction - y / 2
            lhs = total_force_Z_direction * (
                (1 + ((6 * ex) / x) + ((6 * ey) / y)) / (x * y)
            )
            lower = self.soil_bearing_capacity - 10
            if round(lhs) in range(lower, self.soil_bearing_capacity):
                break
        minimum_area = x * y
        return round(minimum_area, 3)

    def pad_base_pressures_sls(self):
        """
        Calculates the pad foundation pressures at the four corners of the foundation using the serviceability limit state
        combination.

        Returns
        -------
        q1 : float
            base pressure at sls located at the bottom left corner of the pad foundation in kN/m2
        q2 : float
            base pressure at sls located at the top left corner of the pad foundation in kN/m2
        q3 : float
            base pressure at sls located at the bottom right corner of the pad foundation in kN/m2
        q4 : float
            base pressure at sls located at the top right corner of the pad foundation in kN/m2
        """
        q1 = self.total_force_Z_dir_sls() * (
            (
                1
                - (
                    6
                    * (
                        self.eccentricity_X_direction_sls()
                        / (self.foundation_length * 1000)
                    )
                )
                - (
                    6
                    * (
                        self.eccentricity_Y_direction_sls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q2 = self.total_force_Z_dir_sls() * (
            (
                1
                - (
                    6
                    * (
                        self.eccentricity_X_direction_sls()
                        / (self.foundation_length * 1000)
                    )
                )
                + (
                    6
                    * (
                        self.eccentricity_Y_direction_sls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q3 = self.total_force_Z_dir_sls() * (
            (
                1
                + (
                    6
                    * (
                        self.eccentricity_X_direction_sls()
                        / (self.foundation_length * 1000)
                    )
                )
                - (
                    6
                    * (
                        self.eccentricity_Y_direction_sls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q4 = self.total_force_Z_dir_sls() * (
            (
                1
                + (
                    6
                    * (
                        self.eccentricity_X_direction_sls()
                        / (self.foundation_length * 1000)
                    )
                )
                + (
                    6
                    * (
                        self.eccentricity_Y_direction_sls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q1 = round(q1, 3)
        q2 = round(q2, 3)
        q3 = round(q3, 3)
        q4 = round(q4, 3)
        return q1, q2, q3, q4

    def bearing_pressure_check_sls(self):
        """
        Checks that calculated foundation pressure does not exceed the allowable bearing pressure supplied at serviceability
        limit state.

        Returns
        -------
        string
            status of the foundation indicating pass or fail.
        """
        minimum_pad_pressure = min(self.pad_base_pressures_sls())
        maximum_pad_pressure = max(self.pad_base_pressures_sls())
        if (minimum_pad_pressure <= self.soil_bearing_capacity) and (
            maximum_pad_pressure <= self.soil_bearing_capacity
        ):
            status = print(
                "PASS - Presumed bearing capacity exceeds design base pressure"
            )
        else:
            status = print(
                "Fail - Presumed bearing capacity lesser than design base pressure"
            )
        return status

    def plot_base_pressures_sls(self):
        """Plots the foundation pressures at each corners of the foundation using the serviceability limit state combination."""
        fig_plan = go.Figure()

        # length is in x direction, width in y direction
        y = [0, 0, self.foundation_width, self.foundation_width, 0]
        x = [0, self.foundation_length, self.foundation_length, 0, 0]

        x_col = [
            self.col_pos_xdir - self.column_length / 2,
            self.col_pos_xdir + self.column_length / 2,
            self.col_pos_xdir + self.column_length / 2,
            self.col_pos_xdir - self.column_length / 2,
            self.col_pos_xdir - self.column_length / 2,
        ]
        y_col = [
            self.col_pos_ydir - self.column_width / 2,
            self.col_pos_ydir - self.column_width / 2,
            self.col_pos_ydir + self.column_width / 2,
            self.col_pos_ydir + self.column_width / 2,
            self.col_pos_ydir - self.column_width / 2,
        ]
        pressure_text = list(self.pad_base_pressures_sls())
        new_pressure_text = []
        for text in range(0, len(pressure_text)):
            new_pressure_text.append(str(pressure_text[text]))

        fig_plan.add_trace(
            go.Scatter(
                x=x,
                y=y,
                name="FOOTING",
                mode="lines+text",
                line=dict(color="red", width=1.5),
                text=new_pressure_text,
                textposition="top center",
            )
        )
        fig_plan.add_trace(
            go.Scatter(
                x=x_col,
                y=y_col,
                name="COLUMN",
                mode="lines",
                line=dict(color="green", width=1.5),
            )
        )

        fig_plan.update_layout(
            title_text="FOOTING PLAN", width=500, height=500, showlegend=True
        )
        fig_plan.show()

    def total_force_X_dir_uls(self):
        """
        Calculates the total force on the foundation in the x direction using the ultimate limit state combination
        of 1.35gk + 1.5qk + 0wk.

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in x direction in kN
        """
        total = (
            (self.uls_strength_factor_permanent * self.permanent_horizontal_load_xdir)
            + (self.imposed_horizontal_load_xdir * self.uls_strength_factor_imposed)
            + (self.wind_horizontal_load_xdir * self.uls_strength_factor_imposed)
        )
        return round(total, 3)

    def total_force_Y_dir_uls(self):
        """
        Calculates the total force on the foundation in the y direction using the ultimate limit state combination
        of 1.35gk + 1.5qk + 0wk.

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in y direction in kN
        """
        total = (
            (self.uls_strength_factor_permanent * self.permanent_horizontal_load_ydir)
            + (self.imposed_horizontal_load_ydir * self.uls_strength_factor_imposed)
            + (self.wind_horizontal_load_ydir * self.uls_strength_factor_imposed)
        )
        return round(total, 3)

    def total_force_Z_dir_uls(self):
        """
        Calculates the total axial force at ultimate limit states of 1.35gk + 1.5qk + 0wk
        The foundation loads are converted to kN and added to the total axial loads from permanent,imposed and wind loads.

        Returns
        -------
        float
            sum of permanent,imposed and wind axial loads including foundation loads in kN
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )
        total = (
            (self.uls_strength_factor_imposed * self.imposed_axial_load)
            + (self.uls_strength_factor_imposed * self.wind_axial_load)
            + self.uls_strength_factor_permanent
            * (
                (self.permanent_axial_load)
                + (self.area_of_foundation() * (fdn_loads[0] + fdn_loads[1]))
            )
        )
        return round(total, 3)

    def total_moments_X_direction_uls(self):
        """
        Calculates the total moments on the foundation in the X direction using the ultimate limit state combination.

        Returns
        -------
        float
            total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )

        Mdx = (
            self.uls_strength_factor_permanent
            * (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * self.foundation_length
                / 2
                + (self.permanent_axial_load * self.col_pos_xdir)
            )
            + self.uls_strength_factor_permanent * (self.permanent_moment_xdir)
            + self.uls_strength_factor_imposed
            * self.imposed_axial_load
            * self.col_pos_xdir
            + self.uls_strength_factor_imposed * self.imposed_moment_xdir
            + self.uls_strength_factor_imposed
            * self.wind_axial_load
            * self.col_pos_xdir
            + self.uls_strength_factor_imposed * self.wind_moments_xdir
            + (
                self.uls_strength_factor_permanent * self.permanent_horizontal_load_xdir
                + self.uls_strength_factor_imposed * self.imposed_horizontal_load_xdir
                + self.uls_strength_factor_imposed * self.wind_horizontal_load_xdir
            )
            * self.foundation_thickness
        )
        return round(Mdx, 3)

    def total_moments_Y_direction_uls(self):
        """
        Calculates the total moments on the foundation in the Y direction using the ultimate limit state combination.

        Returns
        -------
        float
            total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
        )

        Mdy = (
            self.uls_strength_factor_permanent
            * (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * self.foundation_width
                / 2
                + (self.permanent_axial_load * self.col_pos_ydir)
            )
            + self.uls_strength_factor_permanent * self.permanent_moment_ydir
            + self.uls_strength_factor_imposed
            * self.imposed_axial_load
            * self.col_pos_ydir
            + self.uls_strength_factor_imposed_unfavourable * self.imposed_moment_ydir
            + self.uls_strength_factor_imposed
            * self.wind_axial_load
            * self.col_pos_ydir
            + self.uls_strength_factor_imposed * self.wind_moments_ydir
            + (
                self.uls_strength_factor_permanent * self.permanent_horizontal_load_ydir
                + self.uls_strength_factor_imposed * self.imposed_horizontal_load_ydir
                + self.uls_strength_factor_imposed * self.wind_horizontal_load_ydir
            )
            * self.foundation_thickness
        )
        return round(Mdy, 3)

    def eccentricity_X_direction_uls(self):
        """
        Calculates the foundation eccentricity in the X direction using the ultimate limit state combination.

        Returns
        -------
        float
            the eccentricity of the foundation in x direction units are in mm.
        """
        ex = (self.total_moments_X_direction_uls() / self.total_force_Z_dir_uls()) - (
            self.foundation_length / 2
        )
        return round(ex * 1000, 3)

    def eccentricity_Y_direction_uls(self):
        """
        Calculates the foundation eccentricity in the Y direction using the ultimate limit state combination.

        Returns
        -------
        float
            the eccentricity of the foundation in y direction units are in mm.
        """
        ey = (self.total_moments_Y_direction_uls() / self.total_force_Z_dir_uls()) - (
            self.foundation_width / 2
        )
        return round(ey * 1000, 3)

    def pad_base_pressures_uls(self):
        """
        Calculates the pad foundation pressures at the four corners of the foundation using the ultimate limit state
        combination.

        Returns
        -------
        q1 : float
            base pressure at sls located at the bottom left corner of the pad foundation in kN/m2
        q2 : float
            base pressure at sls located at the top left corner of the pad foundation in kN/m2
        q3 : float
            base pressure at sls located at the bottom right corner of the pad foundation in kN/m2
        q4 : float
            base pressure at sls located at the top right corner of the pad foundation in kN/m2
        """
        q1 = self.total_force_Z_dir_uls() * (
            (
                1
                - (
                    6
                    * (
                        self.eccentricity_X_direction_uls()
                        / (self.foundation_length * 1000)
                    )
                )
                - (
                    6
                    * (
                        self.eccentricity_Y_direction_uls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q2 = self.total_force_Z_dir_uls() * (
            (
                1
                - (
                    6
                    * (
                        self.eccentricity_X_direction_uls()
                        / (self.foundation_length * 1000)
                    )
                )
                + (
                    6
                    * (
                        self.eccentricity_Y_direction_uls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q3 = self.total_force_Z_dir_uls() * (
            (
                1
                + (
                    6
                    * (
                        self.eccentricity_X_direction_uls()
                        / (self.foundation_length * 1000)
                    )
                )
                - (
                    6
                    * (
                        self.eccentricity_Y_direction_uls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q4 = self.total_force_Z_dir_uls() * (
            (
                1
                + (
                    6
                    * (
                        self.eccentricity_X_direction_uls()
                        / (self.foundation_length * 1000)
                    )
                )
                + (
                    6
                    * (
                        self.eccentricity_Y_direction_uls()
                        / (self.foundation_width * 1000)
                    )
                )
            )
            / self.area_of_foundation()
        )
        q1 = round(q1, 3)
        q2 = round(q2, 3)
        q3 = round(q3, 3)
        q4 = round(q4, 3)
        return q1, q2, q3, q4

    def base_pressure_rate_of_change_X(self):
        """
        Calculates the rate of change of the base pressure at each meter of the foundation length using Ultimate Limit
        State combination.This would be used for analysing the shear and bending moment diagram along X direction.

        Returns
        -------
        left_hand_base_reaction : float
            The base reaction at the left hand side of the foundation along x direction in kN/m
        right_hand_base_reaction : float
            The base reaction at the right hand side of the foundation along x direction in kN/m
        """
        left_hand_base_reaction = (
            (self.pad_base_pressures_uls()[0] + self.pad_base_pressures_uls()[1])
            * self.foundation_width
            / 2
        )
        right_hand_base_reaction = (
            (self.pad_base_pressures_uls()[2] + self.pad_base_pressures_uls()[3])
            * self.foundation_width
            / 2
        )
        left_hand_base_reaction = round(left_hand_base_reaction, 3)
        right_hand_base_reaction = round(right_hand_base_reaction, 3)
        return left_hand_base_reaction, right_hand_base_reaction

    def base_pressure_rate_of_change_Y(self):
        """
        Calculates the rate of change of the base pressure at each meter of the foundation length using Ultimate Limit
        State combination.This would be used for analysing the shear and bending moment diagram along X direction.

        Returns
        -------
        bottom_edge_base_reaction : float
            The base reaction at the bottom edge of the foundation along y direction in kN/m
        top_edge_base_reaction : float
            The base reaction at the top edge of the foundation along y direction in kN/m
        """
        top_edge_base_reaction = (
            (self.pad_base_pressures_uls()[3] + self.pad_base_pressures_uls()[1])
            * self.foundation_length
            / 2
        )
        bottom_edge_base_reaction = (
            (self.pad_base_pressures_uls()[0] + self.pad_base_pressures_uls()[2])
            * self.foundation_length
            / 2
        )
        top_edge_base_reaction = round(top_edge_base_reaction, 3)
        bottom_edge_base_reaction = round(bottom_edge_base_reaction, 3)
        return bottom_edge_base_reaction, top_edge_base_reaction


class padFoundationDesign(PadFoundation):
    """
    Auxiliary class that inherits from the padfoundation class. This class helps to design the foundation.
    The main class should be created before this design class can be called.

    Methods
    -------
    __loading_diagrams_X_dir()
        Creates an analysis model for the foundation that would then be analysed to get the design forces along the x direction.
    __loading_diagrams_Y_dir()
        Creates an analysis model for the foundation that would then be analysed to get the design forces along the y direction.
    plot_foundation_loading_X()
        Shows the load acting on the foundation in the X direction this consists of the soil loads and concrete own load acting as a udl
        over the foundation length and a soil pressure acting underneath the foundation along the foundation length
    plot_foundation_loading_Y()
        Shows the load acting on the foundation in the Y direction this consists of the soil loads and concrete own load acting as a udl
        over the foundation length and a soil pressure acting underneath the foundation along the foundation width
    plot_bending_moment_X()
        Plots the foundation bending moment diagram along X direction showing the design moment at the face of the column
    plot_bending_moment_Y()
        Plots the foundation bending moment diagram along Y direction showing the design moment at the face of the column
    plot_shear_force_X()
        Plots the foundation shear force diagram along X direction showing the design shear force at a distance 1d from the column face
    plot_shear_force_Y()
        Plots the foundation shear force diagram along Y direction showing the design shear force at a distance 1d from the column face
    get_design_moment_X()
        Outputs the design bending moments of the foundation along the x direction at the face of the column
    get_design_moment_Y()
        Outputs the design bending moments of the foundation along the y direction at the face of the column
    get_design_shear_force_X()
        Outputs the design shear force of the foundation, at a distance 1D from the face of the column along the X direction
    get_design_shear_force_Y()
        Outputs the design shear force of the foundation, at a distance 1D from the face of the column along the Y direction
    area_of_steel_reqd_X_dir()
        Calculates the area of steel required along the x direction of the foundation
    __reinforcement_calculations_X_dir()
        Calculatesthe reinforcements to be provided along the x direction of the foundation
    reinforcement_provision_flexure_X_dir ()
        Calculates the area of steel to be provided along the x direction of the foundation
    area_of_steel_reqd_Y_dir()
        Calculates the area of steel required along the y direction of the foundation
    __reinforcement_calculations_Y_dir()
        Calculates the reinforcements to be provided along the y direction of the foundation
    reinforcement_provision_flexure_Y_dir ()
        Calculates the area of steel to be provided along the y direction of the foundation
    tranverse_shear_check_Xdir()
        Checks the adequacy of the shear stress at a distance equal to d from the column face along the X direction
    tranverse_shear_check_Ydir()
        Checks the adequacy of the shear stress at a distance equal to d from the column face along the Y direction
    __punching_shear()
        Calculates Maximum shear resistance and design punching shear resistance at critical locations
    update_punching_shear_stress_factor()
        Updates the punching shear stress factor as per guidelines in clause 6.4.3(6) of the eurocode 2
    punching_shear_column_face()
        Calculates the punching shear at the column face and check for its adequacy
    punching_shear_check_1d()
        Calculates the unching shear at a distance 1d from the column face and check for its adequacy
    punching_shear_check_2d()
        Calculates the punching shear at a distance 2d from the column face and check for its adequacy
    """

    characteristics_friction_angle = 20

    def __init__(
        self,
        PadFoundation,
        fck: float = 25,
        fyk: float = 460,
        concrete_cover: float = 30,
        bar_diameterX: int = 16,
        bar_diameterY: int = 16,
    ):
        """
        Auxilliary class that initializes pad foundation object for design

        Parameters
        ----------
        Padfoundation : class
            Main class for pad foundation analysis
        fck : float, default - 25
            Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
        fyk : float, default - 460
            Characteristic yield strength of reinforcement in N/mm2
        concrete_cover : float, default - 30
            Nominal cover to foundation in mm
        bar_diameterX : int, default - 16
            Assumed bar diameter of the foundation in the x direction in mm. Accepted range of values [8,10,12,16,20,25,32,40]
        bar_diameterY : int, default - 16
            Assumed bar diameter of the foundation in the y direction in mm Accepted range of values [8,10,12,16,20,25,32,40]
        """
        self.PadFoundation = PadFoundation
        self.fck = fck
        self.fyk = fyk
        self.bar_diameterX = bar_diameterX
        self.concrete_cover = concrete_cover
        self.bar_diameterY = bar_diameterY
        self.dx = (
            (self.PadFoundation.foundation_thickness * 1000)
            - concrete_cover
            - (bar_diameterX / 2)
        ) / 1000
        self.dy = (
            (self.PadFoundation.foundation_thickness * 1000)
            - concrete_cover
            - (bar_diameterY / 2)
            - bar_diameterX
        ) / 1000
        self.beta = 0

        # data validation for inputs
        assert_input_range("Fck", fck, [16, 20, 25, 30, 32, 35, 37, 40, 45, 55])
        assert_strictly_positive_number(fyk, "fyk")
        assert_strictly_positive_number(concrete_cover, "concrete cover")
        assert_input_range(
            "bar_diameterX", bar_diameterX, [8, 10, 12, 16, 20, 25, 32, 40]
        )
        assert_input_range(
            "bar_diameterY", bar_diameterY, [8, 10, 12, 16, 20, 25, 32, 40]
        )

    def __loading_diagrams_X_dir(self):
        """
        Creates an analysis model for the foundation that would then be analysed to get the design forces along the x direction.

        Returns
        -------
        Object
            foundation loading diagram in the x direction wrapped around the beam class of the IndeterminateBeam package.
        """
        foundation = Beam(self.PadFoundation.foundation_length)
        a = Support(self.PadFoundation.col_pos_xdir, fixed=(1, 1, 1))
        foundation.add_supports(a)
        left_load = self.PadFoundation.base_pressure_rate_of_change_X()[0] * 1000
        right_load = self.PadFoundation.base_pressure_rate_of_change_X()[1] * 1000
        fdn_loads = self.foundation_loads(
            self.PadFoundation.foundation_thickness * 1000,
            self.PadFoundation.soil_depth_abv_foundation * 1000,
            self.PadFoundation.soil_unit_weight,
            self.PadFoundation.concrete_unit_weight,
        )
        udl = (
            (sum(fdn_loads)) * self.PadFoundation.foundation_width * 1000
        ) * self.PadFoundation.uls_strength_factor_permanent
        if left_load != right_load:
            foundation_load1 = TrapezoidalLoadV(
                force=(left_load, right_load),
                span=(0, self.PadFoundation.foundation_length),
            )
        else:
            foundation_load1 = DistributedLoadV(
                left_load, span=(0, self.PadFoundation.foundation_length)
            )
        foundation_load2 = DistributedLoadV(
            -udl, span=(0, self.PadFoundation.foundation_length)
        )
        foundation.add_loads(foundation_load1, foundation_load2)
        return foundation

    def __loading_diagrams_Y_dir(self):
        """
        Creates an analysis model for the foundation that would then be analysed to get the design forces along the y direction.

        Returns
        -------
        Object
            foundation loading diagram in the y direction wrapped around the beam class of the IndeterminateBeam package.
        """
        foundation = Beam(self.PadFoundation.foundation_width)
        a = Support(self.PadFoundation.col_pos_ydir, fixed=(1, 1, 1))
        foundation.add_supports(a)
        left_load = self.PadFoundation.base_pressure_rate_of_change_Y()[0] * 1000
        right_load = self.PadFoundation.base_pressure_rate_of_change_Y()[1] * 1000
        fdn_loads = self.foundation_loads(
            self.PadFoundation.foundation_thickness * 1000,
            self.PadFoundation.soil_depth_abv_foundation * 1000,
            self.PadFoundation.soil_unit_weight,
            self.PadFoundation.concrete_unit_weight,
        )
        udl = (
            (sum(fdn_loads)) * self.PadFoundation.foundation_length * 1000
        ) * self.PadFoundation.uls_strength_factor_permanent
        if left_load != right_load:
            foundation_load1 = TrapezoidalLoadV(
                force=(left_load, right_load),
                span=(0, self.PadFoundation.foundation_width),
            )
        else:
            foundation_load1 = DistributedLoadV(
                left_load, span=(0, self.PadFoundation.foundation_width)
            )
        foundation_load2 = DistributedLoadV(
            -udl, span=(0, self.PadFoundation.foundation_width)
        )
        foundation.add_loads(foundation_load1, foundation_load2)
        return foundation

    def plot_foundation_loading_X(self):
        """
        Shows the load acting on the foundation in the X direction this consists of the soil loads and concrete
        own load acting as a udl over the foundation length and a soil pressure acting underneath the foundation
        along the foundation length.
        """
        foundationx = self.__loading_diagrams_X_dir()
        fig = foundationx.plot_beam_diagram()
        fig.layout.title.text = "Foundation schematic (length)"
        fig.layout.xaxis.title.text = "Foundation length"
        fig.show()

    def plot_foundation_loading_Y(self):
        """
        Shows the load acting on the foundation in the Y direction this consists of the soil loads and concrete
        own load acting as a udl over the foundation width and a soil pressure acting underneath the foundation
        along the foundation width.
        """
        foundationy = self.__loading_diagrams_Y_dir()
        fig = foundationy.plot_beam_diagram()
        fig.layout.title.text = "Foundation schematic (width)"
        fig.layout.xaxis.title.text = "Foundation width"
        fig.show()

    def plot_bending_moment_X(self):
        """
        Plots the foundation bending moment diagram along X direction showing the design moment at the face of the column.
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x = self.PadFoundation.col_pos_xdir + self.PadFoundation.column_length / 2
        foundation.add_query_points(x)
        fig1 = foundation.plot_bending_moment(reverse_y=True)
        fig1.layout.xaxis.title.text = "Foundation length"
        fig1.show()

    def plot_bending_moment_Y(self):
        """Plot the foundation bending moment diagram along Y direction showing the design moment at the face of the column"""
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        y = self.PadFoundation.col_pos_ydir + self.PadFoundation.column_width / 2
        foundation.add_query_points(y)
        fig2 = foundation.plot_bending_moment(reverse_y=True)
        fig2.layout.xaxis.title.text = "Foundation width"
        fig2.show()

    def plot_shear_force_X(self):
        """
        Plots the foundation shear force diagram along X direction showing the design shear force at a distance 1d
        from the column face.
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x1 = self.PadFoundation.col_pos_xdir - (
            self.PadFoundation.column_length / 2 + self.dx
        )
        x2 = (
            self.PadFoundation.col_pos_xdir
            + self.PadFoundation.column_length / 2
            + self.dx
        )
        foundation.add_query_points(x1, x2)
        fig1 = foundation.plot_shear_force()
        fig1.layout.xaxis.title.text = "Foundation length"
        fig1.show()

    def plot_shear_force_Y(self):
        """
        Plots the foundation shear force diagram along Y direction showing the design shear force at a distance 1d
        from the column face.
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        y1 = self.PadFoundation.col_pos_ydir - (
            self.PadFoundation.column_width / 2 + self.dy
        )
        y2 = (
            self.PadFoundation.col_pos_ydir
            + self.PadFoundation.column_width / 2
            + self.dy
        )
        foundation.add_query_points(y1, y2)
        fig1 = foundation.plot_shear_force()
        fig1.layout.xaxis.title.text = "Foundation width"
        fig1.show()

    def get_design_moment_X(self):
        """
        Outputs the design bending moments of the foundation along the x direction at the face of the column.

        Returns
        -------
        float
            design bending moment in x direction (default unit - kNm)
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x = self.PadFoundation.col_pos_xdir + self.PadFoundation.column_length / 2
        design_bm = foundation.get_bending_moment(x) / 1000
        return round(design_bm, 3)

    def get_design_moment_Y(self):
        """
        Outputs the design bending moments of the foundation along the y direction at the face of the column.

        Returns
        -------
        float
            design bending moment in x direction (default unit - kNm)
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        y = self.PadFoundation.col_pos_ydir + self.PadFoundation.column_width / 2
        design_bm = foundation.get_bending_moment(y) / 1000
        return round(design_bm, 3)

    def get_design_shear_force_X(self):
        """
        Outputs the design shear force of the foundation, at a distance 1D from the face of the column
        along the X direction.

        Returns
        -------
        float
            design shear force in x direction (default unit - kN)
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x1 = self.PadFoundation.col_pos_xdir - (
            self.PadFoundation.column_length / 2 + self.dx
        )
        x2 = (
            self.PadFoundation.col_pos_xdir
            + self.PadFoundation.column_length / 2
            + self.dx
        )
        shearforces = foundation.get_shear_force(x1, x2)
        design_sf = [x / 1000 for x in shearforces]
        design_shear_force = [abs(round(x, 3)) for x in design_sf]
        return max(design_shear_force)

    def get_design_shear_force_Y(self):
        """
        Outputs the design shear force of the foundation, at a distance 1D from the face of the column
        along the Y direction.

        Returns
        -------
        float
            design shear force in y direction (default unit - kN)
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        y1 = self.PadFoundation.col_pos_ydir - (
            self.PadFoundation.column_width / 2 + self.dy
        )
        y2 = (
            self.PadFoundation.col_pos_ydir
            + self.PadFoundation.column_width / 2
            + self.dy
        )
        shearforces = foundation.get_shear_force(y1, y2)
        design_sfy = [x / 1000 for x in shearforces]
        design_shear_force_y = [abs(round(x, 3)) for x in design_sfy]
        return max(design_shear_force_y)

    def area_of_steel_reqd_X_dir(self):
        """
        Calculates the area of steel required along the x direction of the foundation

        Returns
        -------
        float
            area of steel required in the x direction. (default unit mm2/m)
        """
        Med = self.get_design_moment_X()
        area_of_steel_required_calc = bending_reinforcement(
            Med, self.dx, self.fck, self.fyk, self.PadFoundation.foundation_width * 1000
        )
        area_of_steel_required = max(
            area_of_steel_required_calc,
            minimum_steel(
                self.fck, self.fyk, self.PadFoundation.foundation_width * 1000, self.dx
            ),
        )
        area_required_per_m = (
            area_of_steel_required / self.PadFoundation.foundation_width
        )
        return round(area_required_per_m)

    def __reinforcement_calculations_X_dir(self):
        """
        Calculates the reinforcements to be provided along the x direction of the foundation

        Returns
        -------
        list
            Reinforcement provision, steel diameter, steel class, area provided.
        """
        # In developing the web front end version of this code there would be a combobox that includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement based on the area of steel required initially calculated
        as_required = self.area_of_steel_reqd_X_dir()
        result = reinforcement_provision(as_required, self.fyk)
        return result

    def reinforcement_provision_flexure_X_dir(self):
        """
        Calculates the area of steel to be provided along the x direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_X_dir()
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c bottom. The area provided is {area_provided}mm\u00b2/m parallel to the {self.PadFoundation.foundation_length}m side"

    def area_of_steel_reqd_Y_dir(self):
        """
        Calculates the area of steel required along the y direction of the foundation

        Returns
        -------
        float
            area of steel required in the y direction. (default unit mm2/m)
        """
        Med = self.get_design_moment_Y()
        area_of_steel_required_calc = bending_reinforcement(
            Med,
            self.dy,
            self.fck,
            self.fyk,
            self.PadFoundation.foundation_length * 1000,
        )
        area_of_steel_required = max(
            area_of_steel_required_calc,
            minimum_steel(
                self.fck, self.fyk, self.PadFoundation.foundation_length * 1000, self.dy
            ),
        )
        area_required_per_m = (
            area_of_steel_required / self.PadFoundation.foundation_length
        )
        return round(area_required_per_m)

    def __reinforcement_calculations_Y_dir(self):
        """
        Calculates the reinforcements to be provided along the y direction of the foundation

        Returns
        -------
        list
            Reinforcement provision, steel diameter, steel class, area provided.
        """
        # In developing the web front end version of this code there would be a combobox that includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement based on the area of steel required initially calculated
        as_required = self.area_of_steel_reqd_Y_dir()
        result = reinforcement_provision(as_required, self.fyk)
        return result

    def reinforcement_provision_flexure_Y_dir(self):
        """
        Calculates the area of steel to be provided along the y direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_Y_dir()
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c bottom. The area provided is {area_provided}mm\u00b2/m parallel to the {self.PadFoundation.foundation_width}m side"

    def tranverse_shear_check_Xdir(self):
        """
        Checks the adequacy of the shear stress at a distance equal to d from the column face along the X direction

        Returns
        -------
        string
            formatted string showing the Design shear resistance and design shear force for the x direction.
        """
        design_shear_force = self.get_design_shear_force_X()
        px = round(
            (self.__reinforcement_calculations_X_dir()[3]) / (1000 * self.dx * 1000), 5
        )
        vrd_c = shear_stress_check_1d(self.dx * 1000, px, self.fck)
        Vrd_c = round(
            (vrd_c * self.PadFoundation.foundation_width * 1000 * self.dx * 1000)
            / 1000,
            3,
        )
        if Vrd_c > design_shear_force:
            return f"The design shear resistance of {Vrd_c}kN exceeds the design shear force of {design_shear_force}kN - PASS!!!"
        elif Vrd_c < design_shear_force:
            return f"The design shear resistance of {Vrd_c}kN is less than design shear force of {design_shear_force}kN - FAIL!!!, INCREASE DEPTH"

    def tranverse_shear_check_Ydir(self):
        """
        Checks the adequacy of the shear stress at a distance equal to d from the column face along the Y direction.

        Returns
        -------
        string
            formatted string showing the Design shear resistance and design shear force for the Y direction.
        """
        design_shear_force = self.get_design_shear_force_Y()
        py = round(
            (self.__reinforcement_calculations_Y_dir()[3]) / (1000 * self.dx * 1000), 5
        )
        vrd_c = shear_stress_check_1d(self.dy * 1000, py, self.fck)
        Vrd_c = (
            vrd_c * self.PadFoundation.foundation_length * 1000 * self.dx * 1000
        ) / 1000
        if Vrd_c > design_shear_force:
            return f"The design shear resistance of {round(Vrd_c,3)}kN exceeds the design shear force of {design_shear_force}kN - PASS!!!"
        elif Vrd_c < design_shear_force:
            return f"The design shear resistance of {round(Vrd_c,3)}kN is less than design shear force of {design_shear_force}kN - FAIL!!!, INCREASE DEPTH"

    def __punching_shear(self):
        """
        Calculates Maximum shear resistance and design punching shear resistance at critical locations.

        Returns
        -------
        vrd_max : float
            Maximum punching shear resistance according to cl.6.4.5(3)  of the Eurocode 2 in N/mm2
        vrd_c : float
            Design punching shear resistance according to exp.6.47 of the Eurocode 2 in N/mm2
        vrd_c_1d : float
            Design punching shear resistance at 1d according to exp.6.50 of the Eurocode 2 in N/mm2
        """
        strength_reduction_factor = 0.6 * (1 - self.fck / 250)
        average_depth = np.average([self.dy, self.dx])
        acc = 0.85
        fcd = acc * self.fck / 1.5
        vrd_max = 0.5 * strength_reduction_factor * fcd
        px = round(
            (self.__reinforcement_calculations_X_dir()[3]) / (1000 * self.dx * 1000), 5
        )
        py = round(
            (self.__reinforcement_calculations_Y_dir()[3]) / (1000 * self.dy * 1000), 5
        )
        p1 = min(math.sqrt(px * py), 0.02)
        k = min((1 + math.sqrt(0.2 / average_depth)), 2)
        vmin = 0.035 * (k**1.5) * (self.fck**0.5)
        vrd_c = max((0.12 * k * ((100 * p1 * self.fck) ** (1 / 3))), vmin)
        vrd_c_1d = (2 * average_depth / average_depth) * vrd_c
        critical_punching = [vrd_max, vrd_c, vrd_c_1d]
        return [(round(x, 3)) for x in critical_punching]

    def update_punching_shear_stress_factor(self, beta: float = 0):
        """
        Updates the punching shear stress factor as per guidelines in clause 6.4.3(6) of the eurocode 2

        Parameter
        ---------
        beta : float, default - 0
            Punching shear stress factor according to (fig 6.21N). This is used to override the program's calculated
            punching shear stress factor. if not called beta is calculated using description in expression 6.51 of
            the design code.

        Returns
        -------
        float
            value for punching stress factor
        """
        beta_values = [1.5, 1.4, 1.15]
        if beta in beta_values:
            self.beta = beta
            return beta
        elif beta not in beta_values:
            self.beta = 0
            return beta

    def punching_shear_column_face(self):
        """
        Calculates the punching shear at the column face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        column_perimeter = 2 * (
            self.PadFoundation.column_length + self.PadFoundation.column_width
        )
        design_punching_shear_force = (
            self.PadFoundation.uls_strength_factor_permanent
            * self.PadFoundation.permanent_axial_load
        ) + (
            self.PadFoundation.uls_strength_factor_imposed
            * self.PadFoundation.imposed_axial_load
        )
        punching_shear_stress = design_punching_shear_force / (
            column_perimeter * np.average([self.dy, self.dx]) * 1000
        )
        vrd_max = self.__punching_shear()[0]
        if vrd_max > punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 exceeds the design punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - PASS!!!"
        elif vrd_max < punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 is less than the design punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - FAIL!!!"

    def punching_shear_check_1d(self):
        """
        Calculates the punching shear at a distance 1d from the column face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        cx = (
            self.PadFoundation.base_pressure_rate_of_change_X()[1]
            - self.PadFoundation.base_pressure_rate_of_change_X()[0]
        ) / self.PadFoundation.foundation_length
        cy = (
            self.PadFoundation.base_pressure_rate_of_change_Y()[0]
            - self.PadFoundation.base_pressure_rate_of_change_Y()[1]
        ) / self.PadFoundation.foundation_width
        c1 = self.PadFoundation.column_length
        c2 = self.PadFoundation.column_width
        average_depth = np.average([self.dy, self.dx])
        soil_pressure_ult1 = self.PadFoundation.pad_base_pressures_uls()[0]
        eccxa = (
            self.PadFoundation.col_pos_xdir - self.PadFoundation.foundation_length / 2
        )
        eccya = (
            self.PadFoundation.col_pos_ydir - self.PadFoundation.foundation_width / 2
        )
        ult_pressure_punching_shear = (
            soil_pressure_ult1
            + (
                (
                    self.PadFoundation.foundation_length / 2
                    + eccxa
                    - self.PadFoundation.column_length / 2
                    - average_depth
                )
                + 0.5 * (self.PadFoundation.foundation_length + 2 * average_depth)
            )
            * cx
            / self.PadFoundation.foundation_width
            - (
                (
                    self.PadFoundation.foundation_width / 2
                    + eccya
                    - self.PadFoundation.column_width / 2
                    - average_depth
                )
                + 0.5 * (self.PadFoundation.foundation_width + 2 * average_depth)
            )
            * cy
            / self.PadFoundation.foundation_length
        )
        area = (
            (c1 * c2) + 2 * (c1 + c2) * average_depth + (math.pi * average_depth**2)
        )
        perimeter_length = 2 * (c1 + c2 + (math.pi * average_depth))
        fdn_loads = self.foundation_loads(
            self.PadFoundation.foundation_thickness * 1000,
            self.PadFoundation.soil_depth_abv_foundation * 1000,
            self.PadFoundation.soil_unit_weight,
            self.PadFoundation.concrete_unit_weight,
        )
        fdn_loads_ult = 1.35 * sum(fdn_loads) * self.PadFoundation.area_of_foundation()
        column_axial_load = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_axial_load
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_axial_load
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_axial_load
            )
        )
        design_punching_shear_force = (
            column_axial_load
            + (
                (fdn_loads_ult / self.PadFoundation.area_of_foundation())
                - ult_pressure_punching_shear
            )
            * area
        )
        column_ult_moment_Xdir = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_moment_xdir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_moment_xdir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_moments_xdir
            )
        )
        column_ult_moment_Ydir = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_moment_ydir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_moment_ydir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_moments_ydir
            )
        )
        design_punching_shear_force_eff = design_punching_shear_force * (
            1
            + 1
            * abs(column_ult_moment_Xdir)
            / design_punching_shear_force
            * self.PadFoundation.column_width
            + 1
            * abs(column_ult_moment_Ydir)
            / design_punching_shear_force
            * self.PadFoundation.column_length
        )
        ved = (design_punching_shear_force_eff * 1000) / (
            perimeter_length * average_depth * 1000000
        )
        if (
            self.PadFoundation.eccentricity_X_direction_uls() == 0
            and self.PadFoundation.eccentricity_Y_direction_uls() == 0
        ):
            ved_design = ved
        elif (
            self.PadFoundation.eccentricity_X_direction_uls() != 0
            or self.PadFoundation.eccentricity_Y_direction_uls() != 0
        ):
            column_ratio = c1 / c2
            if column_ratio <= 0.5:
                column_ratio = 0.5
            elif column_ratio >= 3:
                column_ratio = 3
            k = column_punching_coefficient_k(column_ratio)
            W = (
                c1 * c2
                + (2 * c2 * average_depth)
                + (0.5 * c1**2)
                + (4 * average_depth**2)
                + (math.pi * c1 * average_depth)
            )
            foundation_moments = abs(column_ult_moment_Xdir + column_ult_moment_Ydir)
            if self.beta == 0:
                beta = 1 + (
                    k
                    * (foundation_moments / design_punching_shear_force_eff)
                    * (perimeter_length / W)
                )
            elif self.beta != 0:
                beta = self.beta
            ved_design = ved * beta
        if self.__punching_shear()[2] > ved_design:
            return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2 exceeds the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - PASS!!!"
        elif self.__punching_shear()[2] < ved_design:
            return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2 is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"

    def punching_shear_check_2d(self):
        """
        Calculates the punching shear at a distance 2d from the column face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        cx = (
            self.PadFoundation.base_pressure_rate_of_change_X()[1]
            - self.PadFoundation.base_pressure_rate_of_change_X()[0]
        ) / self.PadFoundation.foundation_length
        cy = (
            self.PadFoundation.base_pressure_rate_of_change_Y()[0]
            - self.PadFoundation.base_pressure_rate_of_change_Y()[1]
        ) / self.PadFoundation.foundation_width
        c1 = self.PadFoundation.column_length
        c2 = self.PadFoundation.column_width
        average_depth = np.average([self.dy, self.dx])
        soil_pressure_ult1 = self.PadFoundation.pad_base_pressures_uls()[0]
        eccxa = (
            self.PadFoundation.col_pos_xdir - self.PadFoundation.foundation_length / 2
        )
        eccya = (
            self.PadFoundation.col_pos_ydir - self.PadFoundation.foundation_width / 2
        )
        ult_pressure_punching_shear = (
            soil_pressure_ult1
            + (
                (
                    self.PadFoundation.foundation_length / 2
                    + eccxa
                    - self.PadFoundation.column_length / 2
                    - 2 * average_depth
                )
                + 0.5 * (self.PadFoundation.foundation_length + 4 * average_depth)
            )
            * cx
            / self.PadFoundation.foundation_width
            - (
                (
                    self.PadFoundation.foundation_width / 2
                    + eccya
                    - self.PadFoundation.column_width / 2
                    - 2 * average_depth
                )
                + 0.5 * (self.PadFoundation.foundation_width + 4 * average_depth)
            )
            * cy
            / self.PadFoundation.foundation_length
        )
        area = (
            (c1 * c2)
            + 2 * (c1 + c2) * 2 * average_depth
            + (math.pi * (2 * average_depth) ** 2)
        )
        perimeter_length = 2 * (c1 + c2 + (math.pi * 2 * average_depth))
        fdn_loads = self.foundation_loads(
            self.PadFoundation.foundation_thickness * 1000,
            self.PadFoundation.soil_depth_abv_foundation * 1000,
            self.PadFoundation.soil_unit_weight,
            self.PadFoundation.concrete_unit_weight,
        )
        fdn_loads_ult = 1.35 * sum(fdn_loads) * self.PadFoundation.area_of_foundation()
        column_axial_load = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_axial_load
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_axial_load
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_axial_load
            )
        )
        design_punching_shear_force = (
            column_axial_load
            + (
                (fdn_loads_ult / self.PadFoundation.area_of_foundation())
                - ult_pressure_punching_shear
            )
            * area
        )
        column_ult_moment_Xdir = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_moment_xdir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_moment_xdir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_moments_xdir
            )
        )
        column_ult_moment_Ydir = (
            (
                self.PadFoundation.uls_strength_factor_permanent
                * self.PadFoundation.permanent_moment_ydir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.imposed_moment_ydir
            )
            + (
                self.PadFoundation.uls_strength_factor_imposed
                * self.PadFoundation.wind_moments_ydir
            )
        )
        design_punching_shear_force_eff = design_punching_shear_force * (
            1
            + 2
            * abs(column_ult_moment_Xdir)
            / design_punching_shear_force
            * self.PadFoundation.column_width
            + 2
            * abs(column_ult_moment_Ydir)
            / design_punching_shear_force
            * self.PadFoundation.column_length
        )
        ved = (design_punching_shear_force_eff * 1000) / (
            perimeter_length * average_depth * 1000000
        )
        if (
            self.PadFoundation.eccentricity_X_direction_uls() == 0
            and self.PadFoundation.eccentricity_Y_direction_uls() == 0
        ):
            ved_design = ved
        elif (
            self.PadFoundation.eccentricity_X_direction_uls() != 0
            or self.PadFoundation.eccentricity_Y_direction_uls() != 0
        ):
            column_ratio = c1 / c2
            if column_ratio <= 0.5:
                column_ratio = 0.5
            elif column_ratio >= 3:
                column_ratio = 3
            k = column_punching_coefficient_k(column_ratio)
            W = (
                c1 * c2
                + (2 * c2 * 2 * average_depth)
                + (0.5 * c1**2)
                + (4 * (2 * average_depth) ** 2)
                + (math.pi * c1 * 2 * average_depth)
            )
            foundation_moments = abs(column_ult_moment_Xdir + column_ult_moment_Ydir)
            if self.beta == 0:
                beta = 1 + (
                    k
                    * (foundation_moments / design_punching_shear_force_eff)
                    * (perimeter_length / W)
                )
            elif self.beta != 0:
                beta = self.beta
            ved_design = ved * beta
        if self.__punching_shear()[1] > ved_design:
            return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2 exceeds the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - PASS!!!"
        elif self.__punching_shear()[1] < ved_design:
            return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2 is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"

    def sliding_resistance_check(self):
        """
        Calculates the sliding resistance of the foundation due to horizontal loads based on equations contained in section 6.3 of the
        Eurocode 7.

        Returns
        -------
        sliding_resistance : float
            The allowable sliding resistance of the foundation in kN
        fdn_horizontal_loads : float
            The actual horizontal loads acting on the foundation calculated in accordance to section 6.5.3 in kN
        """
        force_x_direction = (
            self.PadFoundation.uls_strength_factor_permanent
            * self.PadFoundation.permanent_horizontal_load_xdir
            + self.PadFoundation.uls_strength_factor_imposed
            * self.PadFoundation.imposed_horizontal_load_xdir
            + self.PadFoundation.uls_strength_factor_imposed
            * self.PadFoundation.wind_horizontal_load_xdir
        )
        force_y_direction = (
            self.PadFoundation.uls_strength_factor_permanent
            * self.PadFoundation.permanent_horizontal_load_ydir
            + self.PadFoundation.uls_strength_factor_imposed
            * self.PadFoundation.imposed_horizontal_load_ydir
            + self.PadFoundation.uls_strength_factor_imposed
            * self.PadFoundation.wind_horizontal_load_ydir
        )
        fdn_loads = self.foundation_loads(
            self.PadFoundation.foundation_thickness * 1000,
            self.PadFoundation.soil_depth_abv_foundation * 1000,
            self.PadFoundation.soil_unit_weight,
            self.PadFoundation.concrete_unit_weight,
        )
        force_z_direction = (
            self.PadFoundation.area_of_foundation() * (fdn_loads[0] + fdn_loads[1])
        ) + self.PadFoundation.permanent_axial_load
        fdn_horizontal_force = (
            (force_x_direction**2) + (force_y_direction**2)
        ) ** 0.5
        x = math.tan(math.radians(20)) / 1
        design_friction_angle = math.atan(x)
        sliding_resistance = force_z_direction * math.tan(design_friction_angle)
        if sliding_resistance > fdn_horizontal_force:
            return f" The allowable sliding resistance {round(sliding_resistance)}kN is greater than the actual horizontal loads {round(fdn_horizontal_force)}kN Status - PASS!!!"
        elif sliding_resistance < fdn_horizontal_force:
            return f" The allowable sliding resistance {round(sliding_resistance)}kN is lesser than the actual horizontal loads {round(fdn_horizontal_force)}kN Status - FAIL!!!"
