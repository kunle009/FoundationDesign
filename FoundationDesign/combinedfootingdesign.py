"""
Main module that contains the main class for Combined footing foundation analysis
and auxillary class for Pad foundation design.
"""

# Standard library imports
import math
import operator

# Third Party Imports
import numpy as np
import plotly.graph_objs as go
from indeterminatebeam import Beam, Support, TrapezoidalLoadV, DistributedLoadV,PointLoad

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


class CombinedFootingAnalysis:
    """
    Represents a rectangular or square pad foundation that can take permanent,variable and wind
    loads.

    This class serves as the main class that helps analyse the foundation to get the forces needed
    to design the foundation against.

    Attributes
    ----------
    uls_strength_factor_permanent : int or float, default 1.35
        Strength factor that is used to estimate permanent loads at ultimate limit state. This value
        is according to the STR combination. In this code, the equation to estimate uls loads has
        been taken according to (Exp. (6.10)) of the Eurocode 1. To access better economy in design,
        this attribute can be changed and set according to equations (6.10a) or (6.10b) from the
        Eurocode.
    uls_strength_factor_imposed : int or float, default 1.5
        Strength factor that is used to estimate imposed loads at ultimate limit state.
        This value is according to the STR combination. In this code, the equation to estimate
        uls loads has been taken according to (Exp. (6.10)) of the Eurocode 1.To access better
        economy in design,this attribute can be changed and set according to equations (6.10a)
        or (6.10b) from the Eurocode.
    uls_strength_factor_imposed_unfavourable : int or float, default 0
        Strength factor that is used to estimate unfavourable imposed loads at ultimate limit
        state for example wind loads. This value is according to the STR combination.
        In this code, the equation to estimate uls loads has been taken according to
        (Exp. (6.10)) of the Eurocode 1.To access better economy in design, this attribute
        can be changed and set according to equations (6.10a) or (6.10b) from the Eurocode.
    """

    uls_strength_factor_permanent = 1.35
    uls_strength_factor_imposed = 1.5
    uls_strength_factor_imposed_unfavourable = 0

    def __init__(
        self,
        foundation_length: float,
        foundation_width: float,
        soil_bearing_capacity: float = 150,
        spacing_btwn_columns: float = 1500,
    ):
        """
        Initializes a combined footing foundation object.

        Parameters
        ----------
        foundation_length : float
            Length of the foundation. The length of the foundation is along the x axis
            (default unit mm). Must be positive and should not be less than 800mm.
        foundation_width : float
            Width of the foundation. The width of the foundation is along the y axis
            (default unit mm). Must be positive and should not be less than 800mm.
        soil_bearing_capacity : float, optional
            Represents the presumed bearing capacity of the foundation.
            (default unit kN/m2) The assumption here is that previous geotechnical calculations
            must have been done to ascertain the soil bearing capacity. This tool cannot analyse
            the bearing capacity in accordance to Eurocode 7. That can be easily done on
            civils.ai website and thereafter the values of presumed bearing capacuty can be inputed
            in here.
        spacing_btwn_columns : float, optional
            Represents the distance between the two columns along the x directions, by default
            1500mm.
        """
        self.foundation_length = foundation_length / 1000
        self.foundation_width = foundation_width / 1000
        self.soil_bearing_capacity = soil_bearing_capacity
        self.spacing_btwn_columns = spacing_btwn_columns / 1000

        # data validation for inputs
        assert_strictly_positive_number(foundation_length, "foundation_length")
        assert_strictly_positive_number(foundation_width, "foundation_width")
        assert_strictly_positive_number(soil_bearing_capacity, "soil_bearing_capacity")
        # data validation for inputs
        assert_input_limit(foundation_length, 800, "foundation length")
        assert_input_limit(foundation_width, 800, "foundation width")

        self.foundation_length = foundation_length / 1000
        self.foundation_width = foundation_width / 1000
        self.column_length = 100
        self.column_width = 100
        self.soil_bearing_capacity = soil_bearing_capacity
        self.foundation_thickness = 0
        self.soil_depth_abv_foundation = 0
        self.soil_unit_weight = 18
        self.concrete_unit_weight = 24
        self.consider_self_weight = True
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
        self.col_pos_xdir = foundation_length / 2
        self.col_pos_ydir = foundation_width / 2
        self.column_1_geometry = []
        self.column_2_geometry = []
        self.column_1_axial_loads = [0, 0, 0]
        self.column_1_horizontal_loads_xdir = [0, 0, 0]
        self.column_1_horizontal_loads_ydir = [0, 0, 0]
        self.column_1_moments_xdir = [0, 0, 0]
        self.column_1_moments_ydir = [0, 0, 0]
        self.column_1_geometry = []
        self.column_2_geometry = []
        self.column_2_axial_loads = [0, 0, 0]
        self.column_2_horizontal_loads_xdir = [0, 0, 0]
        self.column_2_horizontal_loads_ydir = [0, 0, 0]
        self.column_2_moments_xdir = [0, 0, 0]
        self.column_2_moments_ydir = [0, 0, 0]

    def update_column_1_geometry(
        self,
        column_length: float,
        column_width: float,
        col_pos_xdir: float,
        col_pos_ydir: float,
    ):
        """
        Updates the geometry of the first column.

        Parameters
        ----------
        column_length : float
            Length of the column. The length of the column is along the x axis (default unit mm).
            Must be positive and should not be less than 100mm.
        column_width : float
            Width of the column. The width of the column is along the y axis (default unit mm).
            Must be positive and should not be less than 100mm.
        col_pos_xdir : float
            The position of the column along the length of the foundation in the x axis. This is
            used to model eccentric foundations i.e a situation where the column is not placed
            centrally on the foundation. If the column is at the centre of the foundation then
            this value should be equal to the foundation length divided by two.
            Else the distance should be specified. (default unit mm). This value should not
            be greater than the foundation length.
        col_pos_ydir : float
            The position of the column along the width of the foundation in the y axis.
            This is used to model eccentric foundations i.e a situation where the column
            is not placed centrally on the foundation. If the column is at the centre of the
            foundation then this value should be equal to the foundation width divided by two.
            Else the distance should be specified. (default unit mm). This value should not
            be greater than the foundation width.
        """
        self.column_length = column_length / 1000
        self.column_width = column_width / 1000
        self.col_pos_xdir = col_pos_xdir / 1000
        self.col_pos_ydir = col_pos_ydir / 1000

        assert_strictly_positive_number(column_length, "column_length")
        assert_strictly_positive_number(column_width, "column_width")
        assert_strictly_positive_number(col_pos_xdir, "col_pos_xdir")
        assert_strictly_positive_number(col_pos_ydir, "col_pos_ydir")
        assert_input_limit(column_length, 100, "column length")
        assert_input_limit(column_width, 100, "column width")
        assert_maximum_input_limit(
            self.col_pos_xdir, self.foundation_length, "column position x direction"
        )
        assert_maximum_input_limit(
            self.col_pos_ydir, self.foundation_width, "column position y direction"
        )

        self.column_1_geometry.extend(
            (
                self.column_length,
                self.column_width,
                self.col_pos_xdir,
                self.col_pos_ydir,
            )
        )

    def update_column_2_geometry(
        self,
        column_length: float,
        column_width: float,
        col_pos_xdir: float,
        col_pos_ydir: float,
    ):
        """
        Updates the geometry of the second column.

        Parameters
        ----------
        column_length : float
            Length of the column. The length of the column is along the x axis (default unit mm).
            Must be positive and should not be less than 100mm
        column_width : float
            Width of the column. The width of the column is along the y axis (default unit mm).
            Must be positive and should not be less than 100mm
        col_pos_xdir : float
            The position of the column along the length of the foundation in the x axis.
            This is used to model eccentric foundations i.e a situation where the column is not
            placed centrally on the foundation. If the column is at the centre of the foundation
            then this value should be equal to the foundation length divided by two.
            Else the distance should be specified. (default unit mm). This value should not be
            greater than the foundation length.
        col_pos_ydir : float
            The position of the column along the width of the foundation in the y axis.
            This is used to model eccentric foundations i.e a situation where the column is not
            placed centrally on the foundation. If the column is at the centre of the foundation
            then this value should be equal to the foundation width divided by two.
            Else the distance should be specified. (default unit mm). This value should not be
            greater than the foundation width.
        """
        self.column_length = column_length / 1000
        self.column_width = column_width / 1000
        self.col_pos_xdir = col_pos_xdir / 1000
        self.col_pos_ydir = col_pos_ydir / 1000

        assert_strictly_positive_number(column_length, "column_length")
        assert_strictly_positive_number(col_pos_xdir, "col_pos_xdir")
        assert_strictly_positive_number(col_pos_ydir, "col_pos_ydir")

        assert_input_limit(column_length, 100, "column length")
        assert_input_limit(column_width, 100, "column width")
        assert_maximum_input_limit(
            self.col_pos_xdir, self.foundation_length, "column position x direction"
        )
        assert_maximum_input_limit(
            self.col_pos_ydir, self.foundation_width, "column position y direction"
        )

        self.column_2_geometry.extend(
            (
                self.column_length,
                self.column_width,
                self.col_pos_xdir,
                self.col_pos_ydir,
            )
        )

    def update_column_1_axial_loads(
        self,
        permanent_axial_load: float = 0,
        imposed_axial_load: float = 0,
        wind_axial_load: float = 0,
    ):
        """
        Updates the axial loads for the first column including permanent, imposed and wind
        axial loads.

        Parameters
        ----------
        permanent_axial_load : float, optional
            Represents the permanent axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN)., by default 0kN
        imposed_axial_load : float, optional
            Represents the imposed axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN), by default 0kN
        wind_axial_load : float, optional
            Represents the wind axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN), by default 0kN
        """
        self.permanent_axial_load = permanent_axial_load
        self.imposed_axial_load = imposed_axial_load
        self.wind_axial_load = wind_axial_load
        # data validation for inputs
        assert_number(permanent_axial_load, "Permanent Axial Loads")
        assert_number(imposed_axial_load, "Imposed Axial Loads")
        assert_number(wind_axial_load, "Wind Axial Loads")

        self.column_1_axial_loads.clear()
        self.column_1_axial_loads.extend(
            (permanent_axial_load, imposed_axial_load, wind_axial_load)
        )

    def update_column_1_horizontal_loads_xdir(
        self,
        permanent_horizontal_load_xdir: float = 0,
        imposed_horizontal_load_xdir: float = 0,
        wind_horizontal_load_xdir: float = 0,
    ):
        """
        Updates the column horizontal loads for the first column along the X direction.
        This comprises of permanent,imposed and wind horizontal loads.

        Parameters
        ----------
        permanent_horizontal_load_xdir : float, optional
            Represents permanent horizontal loads acting in the x direction at the base of
            the column.Positive loads act from left to right while negative loads loads act
            from right to left.(default unit = kN), by default 0
        imposed_horizontal_load_xdir : float, optional
            Represents imposed horizontal loads acting in the x direction at the base of
            the column.Positive loads act from left to right while negative loads loads act
            from right to left.(default unit = kN), by default 0
        wind_horizontal_load_xdir : float, optional
            Represents wind horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to
            left.(default unit = kN), by default 0
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

        self.column_1_horizontal_loads_xdir.clear()
        self.column_1_horizontal_loads_xdir.extend(
            (
                permanent_horizontal_load_xdir,
                imposed_horizontal_load_xdir,
                wind_horizontal_load_xdir,
            )
        )

    def update_column_1_horizontal_loads_ydir(
        self,
        permanent_horizontal_load_ydir: float = 0,
        imposed_horizontal_load_ydir: float = 0,
        wind_horizontal_load_ydir: float = 0,
    ):
        """
        Updates the column horizontal loads for the first column along the Y direction.
        This comprises of permanent,imposed and wind horizontal loads.

        Parameters
        ----------
        permanent_horizontal_load_ydir : float, optional
            Represents permanent horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
        imposed_horizontal_load_ydir : float, optional
            Represents imposed horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
        wind_horizontal_load_ydir : float, optional
            Represents wind horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
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

        self.column_1_horizontal_loads_ydir.clear()
        self.column_1_horizontal_loads_ydir.extend(
            (
                permanent_horizontal_load_ydir,
                imposed_horizontal_load_ydir,
                wind_horizontal_load_ydir,
            )
        )

    def update_column_1_moments_xdir(
        self,
        permanent_moment_xdir: float = 0,
        imposed_moment_xdir: float = 0,
        wind_moments_xdir: float = 0,
    ):
        """
        Updatess the first column moments along the X direction. This comprises of permanent,
        imposed and wind moments

        Parameters
        ----------
        permanent_moment_xdir : float, optional
            Represents permanent moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to
            left (default unit = kNm), by default 0
        imposed_moment_xdir : float, optional
            Represents imposed moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to
            left (default unit = kNm), by default 0
        wind_moments_xdir : float, optional
            Represents wind moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to
            left (default unit = kNm), by default 0
        """
        self.permanent_moment_xdir = permanent_moment_xdir
        self.imposed_moment_xdir = imposed_moment_xdir
        self.wind_moments_xdir = wind_moments_xdir
        # data validation for inputs
        assert_number(permanent_moment_xdir, "Permanent moments in X direction")
        assert_number(imposed_moment_xdir, "Imposed moments in X direction")
        assert_number(wind_moments_xdir, "Wind moments in X direction")

        self.column_1_moments_xdir.clear()
        self.column_1_moments_xdir.extend(
            (permanent_moment_xdir, imposed_moment_xdir, wind_moments_xdir)
        )

    def update_column_1_moments_ydir(
        self,
        permanent_moment_ydir: float = 0,
        imposed_moment_ydir: float = 0,
        wind_moments_ydir: float = 0,
    ):
        """
        Updates the column moments along the Y direction. This comprises of permanent,imposed and
        wind moments for the first column.

        Parameters
        ----------
        permanent_moment_ydir : float, optional
            Represents permanent moments in the y axis direction acting about the x axis.
            Positive moments act from
            bottom to top while negative moments acts from top to bottom (default unit = kNm).,
            by default 0
        imposed_moment_ydir : float, optional
            Represents imposed moments in the y direction acting about the x axis. Positive moments act
            from bottom to top while negative moments acts from top to bottom (default unit = kNm),
            by default 0
        wind_moments_ydir : float, optional
            Represents wind moments in the y direction acting about the x axis. Positive moments act from
            bottom to top while negative moments acts from top to bottom (default unit = kNm),
            by default 0
        """
        self.permanent_moment_ydir = permanent_moment_ydir
        self.imposed_moment_ydir = imposed_moment_ydir
        self.wind_moments_ydir = wind_moments_ydir
        # data validation for inputs
        assert_number(permanent_moment_ydir, "Permanent moments in Y direction")
        assert_number(imposed_moment_ydir, "Imposed moments in Y direction")
        assert_number(wind_moments_ydir, "Wind moments in Y direction")

        self.column_1_moments_ydir.clear()
        self.column_1_moments_ydir.extend(
            (permanent_moment_ydir, imposed_moment_ydir, wind_moments_ydir)
        )

    def update_column_2_axial_loads(
        self,
        permanent_axial_load: float = 0,
        imposed_axial_load: float = 0,
        wind_axial_load: float = 0,
    ):
        """
        Updates the axial loads for the second column including permanent, imposed and wind axial loads.

        Parameters
        ----------
        permanent_axial_load : float, optional
            Represents the permanent axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN)., by default 0kN
        imposed_axial_load : float, optional
            Represents the imposed axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN), by default 0kN
        wind_axial_load : float, optional
            Represents the wind axial load. Downward forces are positive. Negative for uplift.
            (default unit = kN), by default 0kN
        """
        self.permanent_axial_load = permanent_axial_load
        self.imposed_axial_load = imposed_axial_load
        self.wind_axial_load = wind_axial_load
        # data validation for inputs
        assert_number(permanent_axial_load, "Permanent Axial Loads")
        assert_number(imposed_axial_load, "Imposed Axial Loads")
        assert_number(wind_axial_load, "Wind Axial Loads")

        self.column_2_axial_loads.clear()
        self.column_2_axial_loads.extend(
            (permanent_axial_load, imposed_axial_load, wind_axial_load)
        )

    def update_column_2_horizontal_loads_xdir(
        self,
        permanent_horizontal_load_xdir: float = 0,
        imposed_horizontal_load_xdir: float = 0,
        wind_horizontal_load_xdir: float = 0,
    ):
        """
        Updates the column horizontal loads for the second column along the X direction.
        This comprises of permanent, imposed and wind horizontal loads.

        Parameters
        ----------
        permanent_horizontal_load_xdir : float, optional
            Represents permanent horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left.
            (default unit = kN), by default 0
        imposed_horizontal_load_xdir : float, optional
            Represents imposed horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left.
            (default unit = kN), by default 0
        wind_horizontal_load_xdir : float, optional
            Represents wind horizontal loads acting in the x direction at the base of the column.
            Positive loads act from left to right while negative loads loads act from right to left.
            (default unit = kN), by default 0
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

        self.column_2_horizontal_loads_xdir.clear()
        self.column_2_horizontal_loads_xdir.extend(
            (
                permanent_horizontal_load_xdir,
                imposed_horizontal_load_xdir,
                wind_horizontal_load_xdir,
            )
        )

    def update_column_2_horizontal_loads_ydir(
        self,
        permanent_horizontal_load_ydir: float = 0,
        imposed_horizontal_load_ydir: float = 0,
        wind_horizontal_load_ydir: float = 0,
    ):
        """
        Updates the column horizontal loads for the second column along the Y direction.
        This comprises of permanent,imposed and wind horizontal loads.

        Parameters
        ----------
        permanent_horizontal_load_ydir : float, optional
            Represents permanent horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
        imposed_horizontal_load_ydir : float, optional
            Represents imposed horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
        wind_horizontal_load_ydir : float, optional
            Represents wind horizontal loads acting in the y direction at the base of the column.
            Positive loads act from bottom to top while negative loads loads act from top to bottom.
            (default unit = kN), by default 0
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

        self.column_2_horizontal_loads_ydir.clear()
        self.column_2_horizontal_loads_ydir.extend(
            (
                permanent_horizontal_load_ydir,
                imposed_horizontal_load_ydir,
                wind_horizontal_load_ydir,
            )
        )

    def update_column_2_moments_xdir(
        self,
        permanent_moment_xdir: float = 0,
        imposed_moment_xdir: float = 0,
        wind_moments_xdir: float = 0,
    ):
        """
        Updatess the second column moments along the X direction. This comprises of permanent,
        imposed and wind moments

        Parameters
        ----------
        permanent_moment_xdir : float, optional
            Represents permanent moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to left
            (default unit = kNm), by default 0
        imposed_moment_xdir : float, optional
            Represents imposed moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to left
            (default unit = kNm), by default 0
        wind_moments_xdir : float, optional
            Represents wind moments in the x direction acting about the y axis.
            Positive moments act from left to right while negative moments acts from right to left
            (default unit = kNm), by default 0
        """
        self.permanent_moment_xdir = permanent_moment_xdir
        self.imposed_moment_xdir = imposed_moment_xdir
        self.wind_moments_xdir = wind_moments_xdir
        # data validation for inputs
        assert_number(permanent_moment_xdir, "Permanent moments in X direction")
        assert_number(imposed_moment_xdir, "Imposed moments in X direction")
        assert_number(wind_moments_xdir, "Wind moments in X direction")

        self.column_2_moments_xdir.clear()
        self.column_2_moments_xdir.extend(
            (permanent_moment_xdir, imposed_moment_xdir, wind_moments_xdir)
        )

    def update_column_2_moments_ydir(
        self,
        permanent_moment_ydir: float = 0,
        imposed_moment_ydir: float = 0,
        wind_moments_ydir: float = 0,
    ):
        """
        Updates the column moments along the Y direction. This comprises of permanent,imposed and
        wind moments for the second column.

        Parameters
        ----------
        permanent_moment_ydir : float, optional
            Represents permanent moments in the y axis direction acting about the x axis.
            Positive moments act from bottom to top while negative moments acts from top to bottom
            (default unit = kNm)., by default 0
        imposed_moment_ydir : float, optional
            Represents imposed moments in the y direction acting about the x axis.
            Positive moments act from bottom to top while negative moments acts from top to bottom
            (default unit = kNm), by default 0
        wind_moments_ydir : float, optional
            Represents wind moments in the y direction acting about the x axis.
            Positive moments act from bottom to top while negative moments acts from top to bottom
            (default unit = kNm), by default 0
        """
        self.permanent_moment_ydir = permanent_moment_ydir
        self.imposed_moment_ydir = imposed_moment_ydir
        self.wind_moments_ydir = wind_moments_ydir
        # data validation for inputs
        assert_number(permanent_moment_ydir, "Permanent moments in Y direction")
        assert_number(imposed_moment_ydir, "Imposed moments in Y direction")
        assert_number(wind_moments_ydir, "Wind moments in Y direction")

        self.column_1_moments_ydir.clear()
        self.column_2_moments_ydir.extend(
            (permanent_moment_ydir, imposed_moment_ydir, wind_moments_ydir)
        )

    def foundation_loads(
        self,
        foundation_thickness: float = 300,
        soil_depth_abv_foundation: float = 500,
        soil_unit_weight: float = 18,
        concrete_unit_weight: float = 24,
        consider_self_weight:bool = True 
    ):
        """
        Calculates the foundation self weight which includes the soil weight above the foundation
        in order terms surchage loads and also the self weight of the concrete base.

        Parameters
        ----------
        foundation_thickness : float, optional
            Represents the depth of the foundation. (default unit mm), by default 300mm
        soil_depth_abv_foundation : float, optional
            Represents the depth of soil above the foundation is added to the self weight of the
            footing to arrive at the foundation own loads.(default unit mm). The default value is
            500mm, If this value should not be included in the calculations, then this parameter
            should be explicitly set to zero, by default 500mm
        soil_unit_weight : float, optional
            The default unit weight of the soil is 18kN/mm^3. (default unit kN/mm^3).
        concrete_unit_weight : float, optional
            The default unit weight of the concrete is 24kN/mm^3 (default unit kN/mm^3).
        consider_self_weight : Bool, optional
            If True self weight would be added if False self weight wont be considered

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
        self.consider_self_weight = consider_self_weight

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
        assert_input_limit(concrete_unit_weight, 0, "Concrete Unit Weight")

        if self.consider_self_weight:
            foundation_self_weight = self.foundation_thickness * self.concrete_unit_weight
            soil_weight = self.soil_depth_abv_foundation * self.soil_unit_weight
            x = round(foundation_self_weight, 3), round(soil_weight, 3)
            return list(x)
        else:
            foundation_self_weight = self.foundation_thickness * self.concrete_unit_weight
            soil_weight = self.soil_depth_abv_foundation * self.soil_unit_weight
            x = 0.00, round(soil_weight, 3)
            return list(x)
    
    
    def plot_geometry(self):
        """Plots the geometry of the foundation, showing the column position relative to the pad base"""
        fig_plan = go.Figure()
        y = [0, 0, self.foundation_width, self.foundation_width, 0]
        x = [0, self.foundation_length, self.foundation_length, 0, 0]

        x_col_1 = [
            self.column_1_geometry[2] - self.column_1_geometry[0] / 2,
            self.column_1_geometry[2] + self.column_1_geometry[0] / 2,
            self.column_1_geometry[2] + self.column_1_geometry[0] / 2,
            self.column_1_geometry[2] - self.column_1_geometry[0] / 2,
            self.column_1_geometry[2] - self.column_1_geometry[0] / 2,
        ]
        y_col_1 = [
            self.column_1_geometry[3] - self.column_1_geometry[1] / 2,
            self.column_1_geometry[3] - self.column_1_geometry[1] / 2,
            self.column_1_geometry[3] + self.column_1_geometry[1] / 2,
            self.column_1_geometry[3] + self.column_1_geometry[1] / 2,
            self.column_1_geometry[3] - self.column_1_geometry[1] / 2,
        ]

        x_col_2 = [
            self.column_2_geometry[2] - self.column_2_geometry[0] / 2,
            self.column_2_geometry[2] + self.column_2_geometry[0] / 2,
            self.column_2_geometry[2] + self.column_2_geometry[0] / 2,
            self.column_2_geometry[2] - self.column_2_geometry[0] / 2,
            self.column_2_geometry[2] - self.column_2_geometry[0] / 2,
        ]
        y_col_2 = [
            self.column_2_geometry[3] - self.column_2_geometry[1] / 2,
            self.column_2_geometry[3] - self.column_2_geometry[1] / 2,
            self.column_2_geometry[3] + self.column_2_geometry[1] / 2,
            self.column_2_geometry[3] + self.column_2_geometry[1] / 2,
            self.column_2_geometry[3] - self.column_2_geometry[1] / 2,
        ]
        fig_plan.add_trace(
            go.Scatter(
                x=x, y=y, name="FOOTING", mode="lines", line=dict(color="red", width=3)
            )
        )
        fig_plan.add_trace(
            go.Scatter(
                x=x_col_1,
                y=y_col_1,
                name="COLUMN 1",
                mode="lines",
                line=dict(color="purple", width=2),
            )
        )
        fig_plan.add_trace(
            go.Scatter(
                x=x_col_2,
                y=y_col_2,
                name="COLUMN 2",
                mode="lines",
                line=dict(color="black", width=2),
            )
        )
        fig_plan.update_layout(
            title_text="FOOTING PLAN", width=500, height=500, showlegend=True
        )
        fig_plan.show()

    def area_of_foundation(self):
        """
        Calculates the area of the foundation.

        Returns
        -------
        float
            The area of the foundation in m^2.
        """
        return self.foundation_length * self.foundation_width

    def total_force_X_dir_sls(self):
        """
        Calculates the total force on the foundation in the x direction using the serviceability
        limit state combination of 1.0gk + 1.0qk + 1.0wk

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in x direction in kN
        """
        return sum(
            self.column_1_horizontal_loads_xdir + self.column_2_horizontal_loads_xdir
        )

    def total_force_Y_dir_sls(self):
        """
        Calculates the total force on the foundation in the y direction using the serviceability
        limit state combination of 1.0gk + 1.0qk + 1.0wk

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in y direction in kN
        """
        return sum(
            self.column_1_horizontal_loads_ydir + self.column_2_horizontal_loads_ydir
        )

    def total_force_Z_dir_sls(self):
        """
        Calculates the total axial force at serviceability limit states of 1.0gk + 1.0qk + 1.0wk.
        The foundation loads are converted to kN and added to the total axial loads from permanent,
        imposed and wind loads.

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
            self.consider_self_weight
        )
        return sum(self.column_1_axial_loads + self.column_2_axial_loads) + (
            self.area_of_foundation() * (fdn_loads[0] + fdn_loads[1])
        )

    def total_moments_X_direction_sls(self):
        """
        Calculates the total moments on the foundation in the X direction using the serviceability
        limit state combination.

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
            self.consider_self_weight
        )
        Mdx_column_1 = (
            (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * (self.foundation_length / 2)
            )
            + (self.column_1_axial_loads[0] * self.column_1_geometry[2])
            + self.column_1_moments_xdir[0]
            + (self.column_1_horizontal_loads_xdir[0] * self.foundation_thickness)
            + (self.column_1_axial_loads[1] * self.column_1_geometry[2])
            + self.column_1_moments_xdir[1]
            + (self.column_1_horizontal_loads_xdir[1] * self.foundation_thickness)
            + (self.column_1_axial_loads[2] * self.column_1_geometry[2])
            + self.column_1_moments_xdir[2]
            + (self.column_1_horizontal_loads_xdir[2] * self.foundation_thickness)
        )

        Mdx_column_2 = (
            (self.column_2_axial_loads[0] * self.column_2_geometry[2])
            + self.column_2_moments_xdir[0]
            + (self.column_2_horizontal_loads_xdir[0] * self.foundation_thickness)
            + (self.column_2_axial_loads[1] * self.column_2_geometry[2])
            + self.column_2_moments_xdir[1]
            + (self.column_2_horizontal_loads_xdir[1] * self.foundation_thickness)
            + (self.column_2_axial_loads[2] * self.column_2_geometry[2])
            + self.column_2_moments_xdir[2]
            + (self.column_2_horizontal_loads_xdir[2] * self.foundation_thickness)
        )

        Mdx = Mdx_column_1 + Mdx_column_2

        return round(Mdx, 3)

    def total_moments_Y_direction_sls(self):
        """
        Calculates the total moments on the foundation in the Y direction using the
        serviceability limit state combination.

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
            self.consider_self_weight
        )
        Mdy_column_1 = (
            (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * (self.foundation_width / 2)
            )
            + (self.column_1_axial_loads[0] * self.column_1_geometry[3])
            + self.column_1_moments_ydir[0]
            + (self.column_1_horizontal_loads_ydir[0] * self.foundation_thickness)
            + (self.column_1_axial_loads[1] * self.column_1_geometry[3])
            + self.column_1_moments_ydir[1]
            + (self.column_1_horizontal_loads_ydir[1] * self.foundation_thickness)
            + (self.column_1_axial_loads[2] * self.column_1_geometry[3])
            + self.column_1_moments_ydir[2]
            + (self.column_1_horizontal_loads_ydir[2] * self.foundation_thickness)
        )

        Mdy_column_2 = (
            (self.column_2_axial_loads[0] * self.column_2_geometry[3])
            + self.column_2_moments_ydir[0]
            + (self.column_2_horizontal_loads_ydir[0] * self.foundation_thickness)
            + (self.column_2_axial_loads[1] * self.column_2_geometry[3])
            + self.column_2_moments_ydir[1]
            + (self.column_2_horizontal_loads_ydir[1] * self.foundation_thickness)
            + (self.column_2_axial_loads[2] * self.column_2_geometry[3])
            + self.column_2_moments_ydir[2]
            + (self.column_2_horizontal_loads_ydir[2] * self.foundation_thickness)
        )

        Mdy = Mdy_column_1 + Mdy_column_2
        return round(Mdy, 3)

    def eccentricity_X_direction_sls(self):
        """
        Calculates the foundation eccentricity in the X direction using the serviceability
        limit state combination.

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
        Calculates the foundation eccentricity in the Y direction using the serviceability
        limit state combination.

        Returns
        -------
        float
            the eccentricity of the foundation in y direction units are in mm.
        """
        ey = (self.total_moments_Y_direction_sls() / self.total_force_Z_dir_sls()) - (
            self.foundation_width / 2
        )
        return round(1000 * ey)

    def pad_base_pressures_sls(self):
        """
        Calculates the combined footing foundation pressures at the four corners of the foundation
        using the serviceability limit state
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
        Checks that calculated foundation pressure does not exceed the allowable bearing pressure
        supplied at serviceability
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

    def minimum_area_required_wt_moment(self):
        """
        Calculates the minimum area of base required taking into account the moments
        imposed on the foundation. Should be used as a rough estimate not a definitive guide.

        Returns
        -------
        float
            Minimum Area required in m2.
        """
        for x, y in zip(np.arange(1, 40.5, 0.05), np.arange(1, 40.5, 0.05)):
            x = np.round(x, 3)
            y = np.round(y, 3)
            col1_pos_xdir = (x - self.spacing_btwn_columns) / 2
            col2_pos_xdir = col1_pos_xdir + self.spacing_btwn_columns
            fdn_loads = self.foundation_loads(
                self.foundation_thickness * 1000,
                self.soil_depth_abv_foundation * 1000,
                self.soil_unit_weight,
                self.concrete_unit_weight,
                self.consider_self_weight
            )
            total_force_Z_direction = sum(
                self.column_1_axial_loads + self.column_2_axial_loads
            ) + ((x * y) * (fdn_loads[0] + fdn_loads[1]))
            Mdx = (
                (x * y * (fdn_loads[0] + fdn_loads[1]) * (x / 2))
                + (self.column_1_axial_loads[0] * col1_pos_xdir)
                + self.column_1_moments_xdir[0]
                + (self.column_1_horizontal_loads_xdir[0] * self.foundation_thickness)
                + (self.column_1_axial_loads[1] * col1_pos_xdir)
                + self.column_1_moments_xdir[1]
                + (self.column_1_horizontal_loads_xdir[1] * self.foundation_thickness)
                + (self.column_1_axial_loads[2] * col1_pos_xdir)
                + self.column_1_moments_xdir[2]
                + (self.column_1_horizontal_loads_xdir[2] * self.foundation_thickness)
                + (self.column_2_axial_loads[0] * col2_pos_xdir)
                + self.column_2_moments_xdir[0]
                + (self.column_2_horizontal_loads_xdir[0] * self.foundation_thickness)
                + (self.column_2_axial_loads[1] * col2_pos_xdir)
                + self.column_2_moments_xdir[1]
                + (self.column_2_horizontal_loads_xdir[1] * self.foundation_thickness)
                + (self.column_2_axial_loads[2] * col2_pos_xdir)
                + self.column_2_moments_xdir[2]
                + (self.column_2_horizontal_loads_xdir[2] * self.foundation_thickness)
            )

            Mdy = (
                (x * y * (fdn_loads[0] + fdn_loads[1]) * (y / 2))
                + (self.column_1_axial_loads[0] * y / 2)
                + self.column_1_moments_ydir[0]
                + (self.column_1_horizontal_loads_ydir[0] * self.foundation_thickness)
                + (self.column_1_axial_loads[1] * y / 2)
                + self.column_1_moments_ydir[1]
                + (self.column_1_horizontal_loads_ydir[1] * self.foundation_thickness)
                + (self.column_1_axial_loads[2] * y / 2)
                + self.column_1_moments_ydir[2]
                + (self.column_1_horizontal_loads_ydir[2] * self.foundation_thickness)
                + (self.column_2_axial_loads[0] * y / 2)
                + self.column_2_moments_ydir[0]
                + (self.column_2_horizontal_loads_ydir[0] * self.foundation_thickness)
                + (self.column_2_axial_loads[1] * y / 2)
                + self.column_2_moments_ydir[1]
                + (self.column_2_horizontal_loads_ydir[1] * self.foundation_thickness)
                + (self.column_2_axial_loads[2] * y / 2)
                + self.column_2_moments_ydir[2]
                + (self.column_2_horizontal_loads_ydir[2] * self.foundation_thickness)
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

    def minimum_area_required(self):
        """
        Calculates the minimuma area required for the foundation without considering imposed moments.

        Returns
        -------
        float
            Minimum area in m2.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
            self.consider_self_weight
        )
        total_force_Z_direction = sum(
            self.column_1_axial_loads + self.column_2_axial_loads
        )
        total_soil = sum(fdn_loads)
        min_area = total_force_Z_direction / (self.soil_bearing_capacity - total_soil)
        return round(min_area, 3)

    def foundation_geometry_optimizer(self):
        """
        Calculates the optimal foundation based on the inputed loads. This is an attempt to help
        the user reduce the amount of design base pressure by suggesting the best possible geometry.
        The user can choose to accept or reject this suggestion.

        Returns
        -------
        Col_1_pos_xdir : float
            The best distance for the first column based on the inputed length along x direction.
        Col_2_pos_xdir : float
            The best distance for the second column based on the inputed length along x direction.
        Col_y
            The best distance for the second column based on the inputed length along y direction.
        """
        try:
            x = self.foundation_length
            y = self.foundation_width
            col1_pos_xdir = np.arange(0, x - self.spacing_btwn_columns, 0.005)
            col2_pos_xdir = np.arange(0 + self.spacing_btwn_columns, x, 0.005)
            col_x1 = col1_pos_xdir.size
            col_x2 = col2_pos_xdir.size
            column_positions = list(map(list, zip(col1_pos_xdir, col2_pos_xdir)))
            column_positions_ydir = np.arange(0, y, 0.005)
            col_y = column_positions_ydir.size
            ex_keys = []
            ey_keys = []
            for i, j in zip(range(0, col_x1), range(0, col_x2)):
                fdn_loads = self.foundation_loads(
                    self.foundation_thickness * 1000,
                    self.soil_depth_abv_foundation * 1000,
                    self.soil_unit_weight,
                    self.concrete_unit_weight,
                    self.consider_self_weight
                )
                total_force_Z_direction = sum(
                    self.column_1_axial_loads + self.column_2_axial_loads
                ) + ((x * y) * (fdn_loads[0] + fdn_loads[1]))
                Mdx = (
                    (x * y * (fdn_loads[0] + fdn_loads[1]) * (x / 2))
                    + (self.column_1_axial_loads[0] * col1_pos_xdir[i])
                    + self.column_1_moments_xdir[0]
                    + (
                        self.column_1_horizontal_loads_xdir[0]
                        * self.foundation_thickness
                    )
                    + (self.column_1_axial_loads[1] * col1_pos_xdir[i])
                    + self.column_1_moments_xdir[1]
                    + (
                        self.column_1_horizontal_loads_xdir[1]
                        * self.foundation_thickness
                    )
                    + (self.column_1_axial_loads[2] * col1_pos_xdir[i])
                    + self.column_1_moments_xdir[2]
                    + (
                        self.column_1_horizontal_loads_xdir[2]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[0] * col2_pos_xdir[j])
                    + self.column_2_moments_xdir[0]
                    + (
                        self.column_2_horizontal_loads_xdir[0]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[1] * col2_pos_xdir[j])
                    + self.column_2_moments_xdir[1]
                    + (
                        self.column_2_horizontal_loads_xdir[1]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[2] * col2_pos_xdir[j])
                    + self.column_2_moments_xdir[2]
                    + (
                        self.column_2_horizontal_loads_xdir[2]
                        * self.foundation_thickness
                    )
                )
                ex = (Mdx / total_force_Z_direction - x / 2) * 1000
                ex_keys.append(ex)
            column_positions_dicts = {
                k: v for (k, v) in zip(ex_keys, column_positions) if k < 0
            }
            new_positions_x = list(
                max(column_positions_dicts.items(), key=operator.itemgetter(1))[1]
            )

            for i in range(0, col_y):
                fdn_loads = self.foundation_loads(
                    self.foundation_thickness * 1000,
                    self.soil_depth_abv_foundation * 1000,
                    self.soil_unit_weight,
                    self.concrete_unit_weight,
                    self.consider_self_weight
                )
                Mdy = (
                    (x * y * (fdn_loads[0] + fdn_loads[1]) * (y / 2))
                    + (self.column_1_axial_loads[0] * column_positions_ydir[i])
                    + self.column_1_moments_ydir[0]
                    + (
                        self.column_1_horizontal_loads_ydir[0]
                        * self.foundation_thickness
                    )
                    + (self.column_1_axial_loads[1] * column_positions_ydir[i])
                    + self.column_1_moments_ydir[1]
                    + (
                        self.column_1_horizontal_loads_ydir[1]
                        * self.foundation_thickness
                    )
                    + (self.column_1_axial_loads[2] * column_positions_ydir[i])
                    + self.column_1_moments_ydir[2]
                    + (
                        self.column_1_horizontal_loads_ydir[2]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[0] * column_positions_ydir[i])
                    + self.column_2_moments_ydir[0]
                    + (
                        self.column_2_horizontal_loads_ydir[0]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[1] * column_positions_ydir[i])
                    + self.column_2_moments_ydir[1]
                    + (
                        self.column_2_horizontal_loads_ydir[1]
                        * self.foundation_thickness
                    )
                    + (self.column_2_axial_loads[2] * column_positions_ydir[i])
                    + self.column_2_moments_ydir[2]
                    + (
                        self.column_2_horizontal_loads_ydir[2]
                        * self.foundation_thickness
                    )
                )
                ey = (Mdy / total_force_Z_direction - y / 2) * 1000
                ey_keys.append(ey)
            column_positions_y_dicts = {
                k: v for (k, v) in zip(ey_keys, column_positions_ydir) if k < 0
            }
            new_positions_y = [
                max(column_positions_y_dicts.items(), key=operator.itemgetter(1))[1]
            ]
            new_col_positions = new_positions_x + new_positions_y
            formatted_col_positions = list(np.around(np.array(new_col_positions), 4))
            return formatted_col_positions
        except ValueError:
            return "The geometry cannot be optimized by this algorithm."

    def plot_optimized_geometry(self):
        """
        Plots the optimized geometry.

        Returns
        -------
        Plot
            Plotly plots showing the directions on the columns.
        """
        try:
            col1_pos_xdir = self.foundation_geometry_optimizer()[0]
            col2_pos_xdir = self.foundation_geometry_optimizer()[1]
            col12_pos_ydir = self.foundation_geometry_optimizer()[2]

            fig_plan = go.Figure()
            y = [0, 0, self.foundation_width, self.foundation_width, 0]
            x = [0, self.foundation_length, self.foundation_length, 0, 0]

            x_col_1 = [
                col1_pos_xdir - self.column_1_geometry[0] / 2,
                col1_pos_xdir + self.column_1_geometry[0] / 2,
                col1_pos_xdir + self.column_1_geometry[0] / 2,
                col1_pos_xdir - self.column_1_geometry[0] / 2,
                col1_pos_xdir - self.column_1_geometry[0] / 2,
            ]
            y_col_1 = [
                col12_pos_ydir - self.column_1_geometry[1] / 2,
                col12_pos_ydir - self.column_1_geometry[1] / 2,
                col12_pos_ydir + self.column_1_geometry[1] / 2,
                col12_pos_ydir + self.column_1_geometry[1] / 2,
                col12_pos_ydir - self.column_1_geometry[1] / 2,
            ]
            x_col_2 = [
                col2_pos_xdir - self.column_2_geometry[0] / 2,
                col2_pos_xdir + self.column_2_geometry[0] / 2,
                col2_pos_xdir + self.column_2_geometry[0] / 2,
                col2_pos_xdir - self.column_2_geometry[0] / 2,
                col2_pos_xdir - self.column_2_geometry[0] / 2,
            ]
            y_col_2 = [
                col12_pos_ydir - self.column_2_geometry[1] / 2,
                col12_pos_ydir - self.column_2_geometry[1] / 2,
                col12_pos_ydir + self.column_2_geometry[1] / 2,
                col12_pos_ydir + self.column_2_geometry[1] / 2,
                col12_pos_ydir - self.column_2_geometry[1] / 2,
            ]

            fig_plan.add_trace(
                go.Scatter(
                    x=x,
                    y=y,
                    name="FOOTING",
                    mode="lines",
                    line=dict(color="red", width=3),
                )
            )
            fig_plan.add_trace(
                go.Scatter(
                    x=x_col_1,
                    y=y_col_1,
                    name="COLUMN 1",
                    mode="lines",
                    line=dict(color="purple", width=2),
                )
            )
            fig_plan.add_trace(
                go.Scatter(
                    x=x_col_2,
                    y=y_col_2,
                    name="COLUMN 2",
                    mode="lines",
                    line=dict(color="black", width=2),
                )
            )
            fig_plan.update_layout(
                title_text="FOOTING PLAN", width=500, height=500, showlegend=True
            )
            fig_plan.show()
        except:
            return self.plot_geometry()

    def total_force_X_dir_uls(self):
        """
        Calculates the total force on the foundation in the x direction using the ultimate limit
        state combination of 1.35gk + 1.5qk + 1.5wk.

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in x direction in kN
        """
        partial_factor_set = [
            self.uls_strength_factor_permanent,
            self.uls_strength_factor_imposed,
            self.uls_strength_factor_imposed,
        ]
        load_sum = [
            sum(loads)
            for loads in zip(
                self.column_1_horizontal_loads_xdir, self.column_2_horizontal_loads_xdir
            )
        ]
        total_loads = np.sum(np.multiply(partial_factor_set, load_sum))
        return total_loads

    def total_force_Y_dir_uls(self):
        """
        Calculates the total force on the foundation in the y direction using the ultimate limit
        state combination of 1.35gk + 1.5qk + 1.5wk.

        Returns
        -------
        float
            sum of permanent,imposed and wind horizontal loads in y direction in kN
        """
        partial_factor_set = [
            self.uls_strength_factor_permanent,
            self.uls_strength_factor_imposed,
            self.uls_strength_factor_imposed,
        ]
        load_sum = [
            sum(loads)
            for loads in zip(
                self.column_1_horizontal_loads_ydir, self.column_2_horizontal_loads_ydir
            )
        ]
        total_loads = np.sum(np.multiply(partial_factor_set, load_sum))
        return total_loads

    def total_force_Z_dir_uls(self):
        """
        Calculates the total axial force at ultimate limit states of 1.35gk + 1.5qk + 1.5wk
        The foundation loads are converted to kN and added to the total axial loads from permanent,
        imposed and wind loads.

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
            self.consider_self_weight
        )
        foundation_loads = [sum(fdn_loads) * self.area_of_foundation(), 0, 0]
        partial_factor_set = [
            self.uls_strength_factor_permanent,
            self.uls_strength_factor_imposed,
            self.uls_strength_factor_imposed,
        ]
        load_sum = [
            sum(loads)
            for loads in zip(
                self.column_1_axial_loads, self.column_2_axial_loads, foundation_loads
            )
        ]
        total_loads = np.sum(np.multiply(partial_factor_set, load_sum))
        return total_loads
    
    def total_axial_force_uls(self):
        """
        Calculates the total axial force at ultimate limit states of 1.35gk + 1.5qk + 1.5wk
        The foundation loads are converted to kN and added to the total axial loads from permanent,
        imposed and wind loads for the individual columns.

        Returns
        -------
        float
            sum of permanent,imposed and wind axial loads including foundation loads in kN
        """
        partial_factor_set = [
            self.uls_strength_factor_permanent,
            self.uls_strength_factor_imposed,
            self.uls_strength_factor_imposed,
        ]
        load_sum_col1 = np.sum(np.multiply(partial_factor_set,self.column_1_axial_loads))
        load_sum_col2 = np.sum(np.multiply(partial_factor_set,self.column_2_axial_loads))
        return [load_sum_col1,load_sum_col2]


    def total_moments_X_direction_uls(self):
        """
        Calculates the total moments on the foundation in the X direction using the ultimate
        limit state combination.

        Returns
        -------
        float
            Total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
            self.consider_self_weight
        )
        Mdx_column_1 = (
            self.uls_strength_factor_permanent
            * (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * (self.foundation_length / 2)
            )
            + self.uls_strength_factor_permanent
            * (self.column_1_axial_loads[0] * self.column_1_geometry[2])
            + (self.uls_strength_factor_permanent * self.column_1_moments_xdir[0])
            + self.uls_strength_factor_permanent
            * (self.column_1_horizontal_loads_xdir[0] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_1_axial_loads[1] * self.column_1_geometry[2])
            + (self.uls_strength_factor_imposed * self.column_1_moments_xdir[1])
            + self.uls_strength_factor_imposed
            * (self.column_1_horizontal_loads_xdir[1] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_1_axial_loads[2] * self.column_1_geometry[2])
            + (self.uls_strength_factor_imposed * self.column_1_moments_xdir[2])
            + self.uls_strength_factor_imposed
            * (self.column_1_horizontal_loads_xdir[2] * self.foundation_thickness)
        )

        Mdx_column_2 = (
            self.uls_strength_factor_permanent
            * (self.column_2_axial_loads[0] * self.column_2_geometry[2])
            + (self.uls_strength_factor_permanent * self.column_2_moments_xdir[0])
            + self.uls_strength_factor_permanent
            * (self.column_2_horizontal_loads_xdir[0] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_2_axial_loads[1] * self.column_2_geometry[2])
            + (self.uls_strength_factor_imposed * self.column_2_moments_xdir[1])
            + self.uls_strength_factor_imposed
            * (self.column_2_horizontal_loads_xdir[1] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_2_axial_loads[2] * self.column_2_geometry[2])
            + (self.uls_strength_factor_imposed * self.column_2_moments_xdir[2])
            + self.uls_strength_factor_imposed
            * (self.column_2_horizontal_loads_xdir[2] * self.foundation_thickness)
        )
        Mdx = Mdx_column_1 + Mdx_column_2
        return round(Mdx, 3)

    def total_moments_Y_direction_uls(self):
        """
        Calculates the total moments on the foundation in the Y direction using the ultimate
        limit state combination.

        Returns
        -------
        float
            Total moments on the foundation in kNm.
        """
        fdn_loads = self.foundation_loads(
            self.foundation_thickness * 1000,
            self.soil_depth_abv_foundation * 1000,
            self.soil_unit_weight,
            self.concrete_unit_weight,
            self.consider_self_weight
        )
        Mdy_column_1 = (
            self.uls_strength_factor_permanent
            * (
                self.area_of_foundation()
                * (fdn_loads[0] + fdn_loads[1])
                * (self.foundation_width / 2)
            )
            + self.uls_strength_factor_permanent
            * (self.column_1_axial_loads[0] * self.column_1_geometry[3])
            + (self.uls_strength_factor_permanent * self.column_1_moments_ydir[0])
            + self.uls_strength_factor_permanent
            * (self.column_1_horizontal_loads_ydir[0] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_1_axial_loads[1] * self.column_1_geometry[3])
            + (self.uls_strength_factor_imposed * self.column_1_moments_ydir[1])
            + self.uls_strength_factor_imposed
            * (self.column_1_horizontal_loads_ydir[1] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_1_axial_loads[2] * self.column_1_geometry[3])
            + (self.uls_strength_factor_imposed * self.column_1_moments_ydir[2])
            + self.uls_strength_factor_imposed
            * (self.column_1_horizontal_loads_ydir[2] * self.foundation_thickness)
        )

        Mdy_column_2 = (
            self.uls_strength_factor_permanent
            * (self.column_2_axial_loads[0] * self.column_2_geometry[3])
            + (self.uls_strength_factor_permanent * self.column_2_moments_ydir[0])
            + self.uls_strength_factor_permanent
            * (self.column_2_horizontal_loads_ydir[0] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_2_axial_loads[1] * self.column_2_geometry[3])
            + (self.uls_strength_factor_imposed * self.column_2_moments_ydir[1])
            + self.uls_strength_factor_imposed
            * (self.column_2_horizontal_loads_ydir[1] * self.foundation_thickness)
            + self.uls_strength_factor_imposed
            * (self.column_2_axial_loads[2] * self.column_2_geometry[3])
            + (self.uls_strength_factor_imposed * self.column_2_moments_ydir[2])
            + self.uls_strength_factor_imposed
            * (self.column_2_horizontal_loads_ydir[2] * self.foundation_thickness)
        )

        Mdy = Mdy_column_1 + Mdy_column_2
        return round(Mdy, 3)

    def eccentricity_X_direction_uls(self):
        """
        Calculates the foundation eccentricity in the X direction using the ultimate
        limit state combination.

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
        Calculates the foundation eccentricity in the Y direction using the ultimate
        limit state combination.

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
        Calculates the combined footing foundation pressures at the four corners of the foundation
        using the ultimate limit state
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
        Calculates the rate of change of the base pressure at each meter of the foundation
        length using Ultimate Limit State combination.This would be used for analysing the shear
        and bending moment diagram along X direction.

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
        Calculates the rate of change of the base pressure at each meter of the foundation length
        using Ultimate Limit State combination.This would be used for analysing the shear and bending
        moment diagram along X direction.

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


class CombinedFootingDesign(CombinedFootingAnalysis):
    """
    Auxiliary class that inherits from the CombinedFootingAnalysis class. This class helps to
    design the foundation.The main class should be created before this design class can be called.

    Parameters
    ----------
    CombinedFootingAnalysis : Class
        Class representing the analysis of the combined foundation.

    """

    characteristics_friction_angle = 20

    def __init__(
        self,
        CombinedFootingAnalysis,
        fck: float = 25,
        fyk: float = 460,
        concrete_cover: float = 30,
        bar_diameterX: int = 16,
        bar_diameterY: int = 16,
    ):
        """
        Auxilliary class that initializes combined foundation object for design.

        Parameters
        ----------
        CombinedFootingAnalysis : Class
            Main class for combined foundation analysis
        fck : float, default - 25
            Characteristic compressive cylinder strength in N/mm2.
            Accepted range of values [16,20,25,30,32,35,37,40,45,55]
        fyk : float, default - 460
            Characteristic yield strength of reinforcement in N/mm2
        concrete_cover : float, default - 30
            Nominal cover to foundation in mm
        bar_diameterX : int, default - 16
            Assumed bar diameter of the foundation in the x direction in mm.
            Accepted range of values [8,10,12,16,20,25,32,40]
        bar_diameterY : int, default - 16
            Assumed bar diameter of the foundation in the y direction in mm.
            Accepted range of values [8,10,12,16,20,25,32,40]
        """
        self.CombinedFootingAnalysis = CombinedFootingAnalysis
        self.fck = fck
        self.fyk = fyk
        self.bar_diameterX = bar_diameterX
        self.concrete_cover = concrete_cover
        self.bar_diameterY = bar_diameterY
        self.dx = (
            (self.CombinedFootingAnalysis.foundation_thickness * 1000)
            - concrete_cover
            - (bar_diameterX / 2)
        ) / 1000
        self.dy = (
            (self.CombinedFootingAnalysis.foundation_thickness * 1000)
            - concrete_cover
            - (bar_diameterY / 2)
            - bar_diameterX
        ) / 1000
        self.beta = 1

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
        Creates an analysis model for the foundation that would then be analysed to get the
        design forces along the x direction.

        Returns
        -------
        Object
            foundation loading diagram in the x direction wrapped around the beam
            class of the IndeterminateBeam package.
        """
        foundation = Beam(self.CombinedFootingAnalysis.foundation_length)
        support_a = Support(
            self.CombinedFootingAnalysis.column_1_geometry[2], (1, 1, 0)
        )
        support_b = Support(
            self.CombinedFootingAnalysis.column_2_geometry[2], (1, 1, 0)
        )
        foundation.add_supports(support_a, support_b)
        left_load = (
            self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[0] * 1000
        )
        right_load = (
            self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[1] * 1000
        )
        fdn_loads = self.foundation_loads(
            self.CombinedFootingAnalysis.foundation_thickness * 1000,
            self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
            self.CombinedFootingAnalysis.soil_unit_weight,
            self.CombinedFootingAnalysis.concrete_unit_weight,
            self.CombinedFootingAnalysis.consider_self_weight
        )
        udl = (
            (sum(fdn_loads)) * self.CombinedFootingAnalysis.foundation_width * 1000
        ) * self.CombinedFootingAnalysis.uls_strength_factor_permanent
        p1 = self.CombinedFootingAnalysis.total_axial_force_uls()[0] * 1000
        p2 = self.CombinedFootingAnalysis.total_axial_force_uls()[1] * 1000
        point_load_1 = PointLoad(force=p1.item(), coord=self.CombinedFootingAnalysis.column_1_geometry[2], angle=-90)
        point_load_2 = PointLoad(force=p2.item(), coord=self.CombinedFootingAnalysis.column_2_geometry[2], angle=-90)
        if left_load != right_load:
            foundation_load1 = TrapezoidalLoadV(
                force=(left_load, right_load),
                span=(0, self.CombinedFootingAnalysis.foundation_length),
            )
        else:
            foundation_load1 = DistributedLoadV(
                left_load, span=(0, self.CombinedFootingAnalysis.foundation_length)
            )
        if sum(fdn_loads) != 0.00:
            foundation_load2 = DistributedLoadV(
                -udl, span=(0, self.CombinedFootingAnalysis.foundation_length)
            )
            foundation.add_loads(foundation_load1, foundation_load2,point_load_1,point_load_2)
        elif sum(fdn_loads) == 0.00:
            foundation.add_loads(foundation_load1,point_load_1,point_load_2)
        return foundation

    def __loading_diagrams_Y_dir(self):
        """
        Creates an analysis model for the foundation that would then be analysed to get
        the design forces along the x direction.

        Returns
        -------
        Object
            foundation loading diagram in the x direction wrapped around the beam class
            of the IndeterminateBeam package.
        """
        foundation = Beam(self.CombinedFootingAnalysis.foundation_width)
        column_1_pos_ydir = self.CombinedFootingAnalysis.column_1_geometry[3]
        column_2_pos_ydir = self.CombinedFootingAnalysis.column_2_geometry[3]

        if column_1_pos_ydir == column_2_pos_ydir:
            support_a = Support(
                self.CombinedFootingAnalysis.column_1_geometry[3], (1, 1, 0)
            )
            foundation.add_supports(support_a)
        elif column_1_pos_ydir != column_2_pos_ydir:
            support_a = Support(
                self.CombinedFootingAnalysis.column_1_geometry[3], (1, 1, 0)
            )
            support_b = Support(
                self.CombinedFootingAnalysis.column_2_geometry[3], (1, 1, 0)
            )
            foundation.add_supports(support_a, support_b)
        left_load = (
            self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[0] * 1000
        )
        right_load = (
            self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[1] * 1000
        )
        fdn_loads = self.foundation_loads(
            self.CombinedFootingAnalysis.foundation_thickness * 1000,
            self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
            self.CombinedFootingAnalysis.soil_unit_weight,
            self.CombinedFootingAnalysis.concrete_unit_weight,
            self.CombinedFootingAnalysis.consider_self_weight
        )
        p1 = self.CombinedFootingAnalysis.total_axial_force_uls()[0] * 1000
        p2 = self.CombinedFootingAnalysis.total_axial_force_uls()[1] * 1000
        point_load_1 = PointLoad(force=p1.item(), coord=self.CombinedFootingAnalysis.column_1_geometry[3], angle=-90)
        point_load_2 = PointLoad(force=p2.item(), coord=self.CombinedFootingAnalysis.column_2_geometry[3], angle=-90)
        udl = (
            (sum(fdn_loads)) * self.CombinedFootingAnalysis.foundation_length * 1000
        ) * self.CombinedFootingAnalysis.uls_strength_factor_permanent
        if left_load != right_load:
            foundation_load1 = TrapezoidalLoadV(
                force=(left_load, right_load),
                span=(0, self.CombinedFootingAnalysis.foundation_width),
            )
        else:
            foundation_load1 = DistributedLoadV(
                left_load, span=(0, self.CombinedFootingAnalysis.foundation_width)
            )
        if sum(fdn_loads) != 0.00:
            foundation_load2 = DistributedLoadV(
                -udl, span=(0, self.CombinedFootingAnalysis.foundation_width)
            )
            foundation.add_loads(foundation_load1, foundation_load2, point_load_1,point_load_2)
        elif sum(fdn_loads) == 0.00:
            foundation.add_loads(foundation_load1, point_load_1,point_load_2)
        return foundation

    def plot_foundation_loading_X(self):
        """
        Shows the load acting on the foundation in the X direction this consists
        of the soil loads and concrete own load acting as a udl over the foundation
        length and a soil pressure acting underneath the foundation along the
        foundation length.
        """
        foundationx = self.__loading_diagrams_X_dir()
        fig = foundationx.plot_beam_diagram()
        fig.layout.title.text = "Foundation schematic (length)"
        fig.layout.xaxis.title.text = "Foundation length"
        fig.show()

    def plot_foundation_loading_Y(self):
        """
        Shows the load acting on the foundation in the Y direction this consists of the soil
        loads and concrete own load acting as a udl over the foundation width and a soil
        pressure acting underneath the foundation along the foundation width.
        """
        foundationy = self.__loading_diagrams_Y_dir()
        fig = foundationy.plot_beam_diagram()
        fig.layout.title.text = "Foundation schematic (width)"
        fig.layout.xaxis.title.text = "Foundation width"
        fig.show()

    def plot_bending_moment_X(self):
        """
        Plots the foundation bending moment diagram along X direction showing the design
        moment at the face of the column.
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        point_1 = (
            self.CombinedFootingAnalysis.column_1_geometry[2]
            - self.CombinedFootingAnalysis.column_1_geometry[0] / 2
        )
        point_2 = (
            self.CombinedFootingAnalysis.column_1_geometry[2]
            + self.CombinedFootingAnalysis.column_1_geometry[0] / 2
        )
        point_3 = (
            self.CombinedFootingAnalysis.column_2_geometry[2]
            - self.CombinedFootingAnalysis.column_2_geometry[0] / 2
        )
        point_4 = (
            self.CombinedFootingAnalysis.column_2_geometry[2]
            + self.CombinedFootingAnalysis.column_2_geometry[0] / 2
        )
        foundation.add_query_points(point_1, point_2, point_3, point_4)
        fig1 = foundation.plot_bending_moment(reverse_y=True)
        fig1.layout.xaxis.title.text = "Foundation length"
        fig1.show()

    def plot_bending_moment_Y(self):
        """Plot the foundation bending moment diagram along Y direction showing the design moment
        at the face of the column"""
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        column_1_pos_ydir = self.CombinedFootingAnalysis.column_1_geometry[3]
        column_2_pos_ydir = self.CombinedFootingAnalysis.column_2_geometry[3]
        if column_1_pos_ydir == column_2_pos_ydir:
            point_1 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_2 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                + self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            foundation.add_query_points(point_1, point_2)
        elif column_1_pos_ydir != column_2_pos_ydir:
            point_1 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_2 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                + self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_3 = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                - self.CombinedFootingAnalysis.column_2_geometry[1] / 2
            )
            point_4 = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                + self.CombinedFootingAnalysis.column_2_geometry[1] / 2
            )
            foundation.add_query_points(point_1, point_2, point_3, point_4)
        fig2 = foundation.plot_bending_moment(reverse_y=True)
        fig2.layout.xaxis.title.text = "Foundation width"
        fig2.show()

    def plot_shear_force_X(self):
        """
        Plots the foundation shear force diagram along X direction showing the design
        shear force at a distance 1d from the column face.
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x1 = self.CombinedFootingAnalysis.column_1_geometry[2] - (
            self.CombinedFootingAnalysis.column_1_geometry[0] / 2 + self.dx
        )
        x2 = self.CombinedFootingAnalysis.column_1_geometry[2] + (
            self.CombinedFootingAnalysis.column_1_geometry[0] / 2 + self.dx
        )
        x3 = self.CombinedFootingAnalysis.column_2_geometry[2] - (
            self.CombinedFootingAnalysis.column_2_geometry[0] / 2 + self.dx
        )
        x4 = self.CombinedFootingAnalysis.column_2_geometry[2] + (
            self.CombinedFootingAnalysis.column_2_geometry[0] / 2 + self.dx
        )
        query_point_list = [x1, x2, x3, x4]
        filtered_query_point_list = [
            query_point for query_point in query_point_list if query_point > 0
        ]
        foundation.add_query_points(*filtered_query_point_list)
        fig1 = foundation.plot_shear_force()
        fig1.layout.xaxis.title.text = "Foundation length"
        fig1.show()

    def plot_shear_force_Y(self):
        """
        Plots the foundation shear force diagram along Y direction showing the design
        shear force at a distance 1d from the column face.
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        column_1_pos_ydir = self.CombinedFootingAnalysis.column_1_geometry[3]
        column_2_pos_ydir = self.CombinedFootingAnalysis.column_2_geometry[3]
        if column_1_pos_ydir == column_2_pos_ydir:
            y1 = self.CombinedFootingAnalysis.column_1_geometry[3] - (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y2 = self.CombinedFootingAnalysis.column_1_geometry[3] + (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            query_point_list = [y1, y2]
            filtered_query_point_list = [
                query_point for query_point in query_point_list if query_point > 0
            ]
            foundation.add_query_points(*filtered_query_point_list)
        elif column_1_pos_ydir != column_2_pos_ydir:
            y1 = self.CombinedFootingAnalysis.column_1_geometry[3] - (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y2 = self.CombinedFootingAnalysis.column_1_geometry[3] + (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y3 = self.CombinedFootingAnalysis.column_2_geometry[3] - (
                self.CombinedFootingAnalysis.column_2_geometry[1] / 2 + self.dy
            )
            y4 = self.CombinedFootingAnalysis.column_2_geometry[3] + (
                self.CombinedFootingAnalysis.column_2_geometry[1] / 2 + self.dy
            )
            query_point_list = [y1, y2, y3, y4]
            filtered_query_point_list = [
                query_point for query_point in query_point_list if query_point > 0
            ]
            foundation.add_query_points(*filtered_query_point_list)
        fig1 = foundation.plot_shear_force()
        fig1.layout.xaxis.title.text = "Foundation Width"
        fig1.show()

    def get_design_moment_X(self):
        """
        Outputs the design bending moments of the foundation along the x direction at
        the face of the column.

        Returns
        -------
        Negative Bending Moment : float
            design bending moment in x direction (default unit - kNm)
        Positive Bending Moment : float
            design bending moment in x direction (default unit - kNm)
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        point_1 = (
            self.CombinedFootingAnalysis.column_1_geometry[2]
            - self.CombinedFootingAnalysis.column_1_geometry[0] / 2
        )
        point_2 = (
            self.CombinedFootingAnalysis.column_1_geometry[2]
            + self.CombinedFootingAnalysis.column_1_geometry[0] / 2
        )
        point_3 = (
            self.CombinedFootingAnalysis.column_2_geometry[2]
            - self.CombinedFootingAnalysis.column_2_geometry[0] / 2
        )
        point_4 = (
            self.CombinedFootingAnalysis.column_2_geometry[2]
            + self.CombinedFootingAnalysis.column_2_geometry[0] / 2
        )
        design_bm_positive = (
            max(foundation.get_bending_moment(*[point_1, point_2, point_3, point_4]))
            / 1000
        )
        design_bm_negative = foundation.get_bending_moment(return_min=True) / 1000
        return [abs(round(bm, 3)) for bm in [design_bm_negative, design_bm_positive]]

    def get_design_moment_Y(self):
        """
        Outputs the design bending moments of the foundation along the y
        direction at the face of the column.

        Returns
        -------
        Negative Bending Moment : float
            design bending moment in x direction (default unit - kNm)
        Positive Bending Moment : float
            design bending moment in x direction (default unit - kNm)
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        column_1_pos_ydir = self.CombinedFootingAnalysis.column_1_geometry[3]
        column_2_pos_ydir = self.CombinedFootingAnalysis.column_2_geometry[3]
        if column_1_pos_ydir == column_2_pos_ydir:
            point_1 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_2 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                + self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            design_bm_positive = (
                max(foundation.get_bending_moment(*[point_1, point_2])) / 1000
            )
        elif column_1_pos_ydir != column_2_pos_ydir:
            point_1 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_2 = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                + self.CombinedFootingAnalysis.column_1_geometry[1] / 2
            )
            point_3 = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                - self.CombinedFootingAnalysis.column_2_geometry[1] / 2
            )
            point_4 = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                + self.CombinedFootingAnalysis.column_2_geometry[1] / 2
            )
            design_bm_positive = (
                max(
                    foundation.get_bending_moment(*[point_1, point_2, point_3, point_4])
                )
                / 1000
            )
        design_bm_negative = foundation.get_bending_moment(return_min=True) / 1000
        return [abs(round(bm, 3)) for bm in [design_bm_negative, design_bm_positive]]

    def get_design_shear_force_X(self):
        """
        Outputs the design shear force of the foundation, at a distance 1D
        from the face of the column along the X direction.

        Returns
        -------
        float
            design shear force in x direction (default unit - kN)
        """
        foundation = self.__loading_diagrams_X_dir()
        foundation.analyse()
        x1 = self.CombinedFootingAnalysis.column_1_geometry[2] - (
            self.CombinedFootingAnalysis.column_1_geometry[0] / 2 + self.dx
        )
        x2 = self.CombinedFootingAnalysis.column_1_geometry[2] + (
            self.CombinedFootingAnalysis.column_1_geometry[0] / 2 + self.dx
        )
        x3 = self.CombinedFootingAnalysis.column_2_geometry[2] - (
            self.CombinedFootingAnalysis.column_2_geometry[0] / 2 + self.dx
        )
        x4 = self.CombinedFootingAnalysis.column_2_geometry[2] + (
            self.CombinedFootingAnalysis.column_2_geometry[0] / 2 + self.dx
        )
        query_point_list = [x1, x2, x3, x4]
        filtered_query_point_list = [
            query_point for query_point in query_point_list if query_point > 0
        ]
        shearforces = foundation.get_shear_force(*filtered_query_point_list)
        design_sf = [x / 1000 for x in shearforces]
        design_shear_force = [abs(round(x, 3)) for x in design_sf]
        return max(design_shear_force)

    def get_design_shear_force_Y(self):
        """
        Outputs the design shear force of the foundation, at a distance 1D
        from the face of the column along the Y direction.

        Returns
        -------
        float
            design shear force in y direction (default unit - kN)
        """
        foundation = self.__loading_diagrams_Y_dir()
        foundation.analyse()
        column_1_pos_ydir = self.CombinedFootingAnalysis.column_1_geometry[3]
        column_2_pos_ydir = self.CombinedFootingAnalysis.column_2_geometry[3]
        if column_1_pos_ydir == column_2_pos_ydir:
            y1 = self.CombinedFootingAnalysis.column_1_geometry[3] - (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y2 = self.CombinedFootingAnalysis.column_1_geometry[3] + (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            query_point_list = [y1, y2]
            filtered_query_point_list = [
                query_point for query_point in query_point_list if query_point > 0
            ]
            shearforces = foundation.get_shear_force(*filtered_query_point_list)
        elif column_1_pos_ydir != column_2_pos_ydir:
            y1 = self.CombinedFootingAnalysis.column_1_geometry[3] - (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y2 = self.CombinedFootingAnalysis.column_1_geometry[3] + (
                self.CombinedFootingAnalysis.column_1_geometry[1] / 2 + self.dy
            )
            y3 = self.CombinedFootingAnalysis.column_2_geometry[3] - (
                self.CombinedFootingAnalysis.column_2_geometry[1] / 2 + self.dy
            )
            y4 = self.CombinedFootingAnalysis.column_2_geometry[3] + (
                self.CombinedFootingAnalysis.column_2_geometry[1] / 2 + self.dy
            )
            query_point_list = [y1, y2, y3, y4]
            filtered_query_point_list = [
                query_point for query_point in query_point_list if query_point > 0
            ]
            shearforces = foundation.get_shear_force(*filtered_query_point_list)
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
        Med = np.array(self.get_design_moment_X())
        area_required_per_m = np.ones(2)
        for i in np.arange(0, 2, 1):
            area_of_steel_required_calc = bending_reinforcement(
                Med[i],
                self.dx,
                self.fck,
                self.fyk,
                self.CombinedFootingAnalysis.foundation_width * 1000,
            )
            area_of_steel_required = max(
                area_of_steel_required_calc,
                minimum_steel(
                    self.fck,
                    self.fyk,
                    self.CombinedFootingAnalysis.foundation_width * 1000,
                    self.dx,
                ),
            )
            area_required_per_m[i] = (
                area_of_steel_required / self.CombinedFootingAnalysis.foundation_width
            )
        return area_required_per_m.round(2)

    def __reinforcement_calculations_X_dir(self):
        """
        Calculates the reinforcements to be provided along the x direction of the foundation

        Returns
        -------
        list
            Reinforcement provision, steel diameter, steel class, area provided.
        """
        # In developing the web front end version of this code there would be a combobox
        # that includes
        # the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that he
        # founds
        # appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement based on
        # the area of steel required initially calculated
        as_required = np.array(self.area_of_steel_reqd_X_dir())
        result = []
        for i in range(0, 2, 1):
            result.append(reinforcement_provision(as_required[i], self.fyk))
        return result

    def reinforcement_prov_flexure_X_dir_TOP(self):
        """
        Calculates the area of steel to be provided along the x direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that
        # includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that
        # he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement
        # based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_X_dir()[0]
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c TOP.The area provided is {area_provided}mm\u00b2/m parallel to the {self.CombinedFootingAnalysis.foundation_length}m side"

    def reinforcement_prov_flexure_X_dir_Bottom(self):
        """
        Calculates the area of steel to be provided along the x direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that
        # includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that
        # he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement
        # based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_X_dir()[1]
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c BOTTOM .\
            The area provided is {area_provided}mm\u00b2/m parallel to the \
                {self.CombinedFootingAnalysis.foundation_length}m side"

    def area_of_steel_reqd_Y_dir(self):
        """
        Calculates the area of steel required along the y direction of the foundation

        Returns
        -------
        float
            area of steel required in the y direction. (default unit mm2/m)
        """
        Med = np.array(self.get_design_moment_Y())
        area_required_per_m = np.ones(2)
        for i in np.arange(0, 2, 1):
            area_of_steel_required_calc = bending_reinforcement(
                Med[i],
                self.dx,
                self.fck,
                self.fyk,
                self.CombinedFootingAnalysis.foundation_length * 1000,
            )
            area_of_steel_required = max(
                area_of_steel_required_calc,
                minimum_steel(
                    self.fck,
                    self.fyk,
                    self.CombinedFootingAnalysis.foundation_length * 1000,
                    self.dx,
                ),
            )
            area_required_per_m[i] = (
                area_of_steel_required / self.CombinedFootingAnalysis.foundation_length
            )
        return area_required_per_m.round(2)

    def __reinforcement_calculations_Y_dir(self):
        """
        Calculates the reinforcements to be provided along the y direction of the foundation

        Returns
        -------
        list
            Reinforcement provision, steel diameter, steel class, area provided.
        """
        # In developing the web front end version of this code there would be a
        # combobox that includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose
        # the steel that he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area
        # of reinforcement based on the area of steel required initially calculated
        as_required = np.array(self.area_of_steel_reqd_Y_dir())
        result = []
        for i in range(0, 2, 1):
            result.append(reinforcement_provision(as_required[i], self.fyk))
        return result

    def reinforcement_prov_flexure_Y_dir_Top(self):
        """
        Calculates the area of steel to be provided along the y direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that
        # includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that
        # he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement
        # based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_Y_dir()[0]
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c TOP. \
            The area provided is {area_provided}mm\u00b2/m parallel to the \
                {self.CombinedFootingAnalysis.foundation_width}m side"

    def reinforcement_prov_flexure_Y_dir_Bottom(self):
        """
        Calculates the area of steel to be provided along the y direction of the foundation

        Returns
        -------
        string
            Formatted string showing steel diameter, steel class, spacing and area provided.
        """
        # In developing the web front end version of this code there would be a combobox that
        # includes the bar diameters and equivalent reinforcement
        # spacing this would give power to the user to enable the user chose the steel that
        # he founds appropriate tp satisfy the reinforcement requirement
        # but for now i have coded a function to automatically select area of reinforcement
        # based on the area of steel required initially calculated
        steel_bars = self.__reinforcement_calculations_Y_dir()[1]
        steel_label = steel_bars[0]
        bar_dia = steel_bars[1]
        bar_spacing = steel_bars[2]
        area_provided = steel_bars[3]
        return f"Provide {steel_label}{bar_dia} bars spaced at {bar_spacing}mm c/c Bottom.The area provided is {area_provided}mm\u00b2/m parallel to the {self.CombinedFootingAnalysis.foundation_width}m side"

    def tranverse_shear_check_Xdir(self):
        """
        Checks the adequacy of the shear stress at a distance equal to d from the column face
        along the X direction.

        Returns
        -------
        string
            formatted string showing the Design shear resistance and design shear force for
            the x direction.
        """
        design_shear_force = self.get_design_shear_force_X()
        as_prov_bot = self.__reinforcement_calculations_X_dir()[1]
        px = round((as_prov_bot[3]) / (1000 * self.dx * 1000), 5)
        vrd_c = shear_stress_check_1d(self.dx * 1000, px, self.fck)
        Vrd_c = round(
            (
                vrd_c
                * self.CombinedFootingAnalysis.foundation_width
                * 1000
                * self.dx
                * 1000
            )
            / 1000,
            3,
        )
        if Vrd_c > design_shear_force:
            return f"The design shear resistance of {Vrd_c}kN exceeds the design\
                shear force of {design_shear_force}kN - PASS!!!"
        elif Vrd_c < design_shear_force:
            return f"The design shear resistance of {Vrd_c}kN is less than design \
                shear force of {design_shear_force}kN - FAIL!!!, INCREASE DEPTH"

    def tranverse_shear_check_Ydir(self):
        """
        Checks the adequacy of the shear stress at a distance equal to d from the column
        face along the Y direction.

        Returns
        -------
        string
            formatted string showing the Design shear resistance and design shear force
            for the Y direction.
        """
        design_shear_force = self.get_design_shear_force_Y()
        as_prov_top = self.__reinforcement_calculations_Y_dir()[1]
        py = round((as_prov_top[3]) / (1000 * self.dx * 1000), 5)
        vrd_c = shear_stress_check_1d(self.dy * 1000, py, self.fck)
        Vrd_c = (
            vrd_c
            * self.CombinedFootingAnalysis.foundation_length
            * 1000
            * self.dx
            * 1000
        ) / 1000
        if Vrd_c > design_shear_force:
            return f"The design shear resistance of {round(Vrd_c,3)}kN exceeds the design \
                shear force of {design_shear_force}kN - PASS!!!"
        elif Vrd_c < design_shear_force:
            return f"The design shear resistance of {round(Vrd_c,3)}kN is less than design\
                shear force of {design_shear_force}kN - FAIL!!!, INCREASE DEPTH"

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
        bottom_reinforcementx = self.__reinforcement_calculations_X_dir()[1]
        top_reinforcementy = self.__reinforcement_calculations_Y_dir()[1]
        px = round((bottom_reinforcementx[3]) / (1000 * self.dx * 1000), 5)
        py = round((top_reinforcementy[3]) / (1000 * self.dy * 1000), 5)
        p1 = min(math.sqrt(px * py), 0.02)
        k = min((1 + math.sqrt(0.2 / average_depth)), 2)
        vmin = 0.035 * (k**1.5) * (self.fck**0.5)
        vrd_c = max((0.12 * k * ((100 * p1 * self.fck) ** (1 / 3))), vmin)
        vrd_c_1d = (2 * average_depth / average_depth) * vrd_c
        critical_punching = [vrd_max, vrd_c, vrd_c_1d]
        return [(round(x, 3)) for x in critical_punching]

    def update_punching_shear_stress_factor(self, beta: float = 0):
        """
        Updates the punching shear stress factor as per guidelines in clause 6.4.3(6) of
        the eurocode 2

        Parameter
        ---------
        beta : float, default - 0
            Punching shear stress factor according to (fig 6.21N). This is used to override
            the program's calculated punching shear stress factor. if not called beta is
            calculated using description in expression 6.51 of the design code.

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
            self.beta = 1
            return beta

    def col_1_punching_shear_column_face(self):
        """
        Calculates the punching shear at the column face and check for its adequacy.

        Return
        ------
        string
            Maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        column_perimeter = 2 * (
            self.CombinedFootingAnalysis.column_1_geometry[0]
            + self.CombinedFootingAnalysis.column_1_geometry[1]
        )
        design_punching_shear_force = (
            (
                self.CombinedFootingAnalysis.uls_strength_factor_permanent
                * self.CombinedFootingAnalysis.column_1_axial_loads[0]
            )
            + (
                self.CombinedFootingAnalysis.uls_strength_factor_imposed
                * self.CombinedFootingAnalysis.column_1_axial_loads[1]
            )
            + (
                self.CombinedFootingAnalysis.uls_strength_factor_imposed
                * self.CombinedFootingAnalysis.column_1_axial_loads[2]
            )
        )
        punching_shear_stress = self.beta * (
            design_punching_shear_force
            / (column_perimeter * np.average([self.dy, self.dx]) * 1000)
        )
        vrd_max = self.__punching_shear()[0]
        if vrd_max > punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 \
                exceeds the design punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - PASS!!!"
        elif vrd_max < punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 \
                is less than the design punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - FAIL!!!"

    def col_1_punching_shear_check_1d(self):
        """
        Calculates the punching shear at a distance 1d from the column one face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        average_depth = np.average([self.dy, self.dx])
        if (average_depth > self.CombinedFootingAnalysis.column_1_geometry[2]) or (
            average_depth > self.CombinedFootingAnalysis.column_1_geometry[3]
        ):
            return None
        elif (average_depth < self.CombinedFootingAnalysis.column_1_geometry[2]) or (
            average_depth < self.CombinedFootingAnalysis.column_1_geometry[3]
        ):
            cx = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[1]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[0]
            ) / self.CombinedFootingAnalysis.foundation_length
            cy = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[0]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[1]
            ) / self.CombinedFootingAnalysis.foundation_width
            c1 = self.CombinedFootingAnalysis.column_1_geometry[0]
            c2 = self.CombinedFootingAnalysis.column_1_geometry[1]
            # average_depth = np.average([self.dy,self.dx])
            soil_pressure_ult1 = self.CombinedFootingAnalysis.pad_base_pressures_uls()[
                0
            ]
            eccxa = (
                self.CombinedFootingAnalysis.column_1_geometry[2]
                - self.CombinedFootingAnalysis.foundation_length / 2
            )
            eccya = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.foundation_width / 2
            )
            ult_pressure_punching_shear = (
                soil_pressure_ult1
                + (
                    (
                        self.CombinedFootingAnalysis.foundation_length / 2
                        + eccxa
                        - self.CombinedFootingAnalysis.column_1_geometry[0] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_length
                        + 2 * average_depth
                    )
                )
                * cx
                / self.CombinedFootingAnalysis.foundation_width
                - (
                    (
                        self.CombinedFootingAnalysis.foundation_width / 2
                        + eccya
                        - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_width
                        + 2 * average_depth
                    )
                )
                * cy
                / self.CombinedFootingAnalysis.foundation_length
            )
            area = (2 * (c1 + c2) * average_depth) + (math.pi * average_depth**2)
            perimeter_length = 2 * (c1 + c2) + 2 * (math.pi * average_depth)
            fdn_loads = self.foundation_loads(
                self.CombinedFootingAnalysis.foundation_thickness * 1000,
                self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
                self.CombinedFootingAnalysis.soil_unit_weight,
                self.CombinedFootingAnalysis.concrete_unit_weight,
            )
            fdn_loads_ult = (
                1.35
                * sum(fdn_loads)
                * self.CombinedFootingAnalysis.area_of_foundation()
            )
            column_axial_load = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_axial_loads[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_axial_loads[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_axial_loads[2]
                )
            )
            design_punching_shear_force = (
                column_axial_load
                + (
                    (
                        (
                            fdn_loads_ult
                            / self.CombinedFootingAnalysis.area_of_foundation()
                        )
                        - ult_pressure_punching_shear
                    )
                )
                * area
            )
            column_ult_moment_Xdir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[2]
                )
            )
            column_ult_moment_Ydir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[2]
                )
            )
            design_punching_shear_force_eff = design_punching_shear_force * (
                1
                + 1
                * abs(column_ult_moment_Xdir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_1_geometry[1]
                + 1
                * abs(column_ult_moment_Ydir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_1_geometry[0]
            )
            ved = (design_punching_shear_force_eff * 1000) / (
                perimeter_length * average_depth * 1000000
            )
            if (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() == 0
                and self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() == 0
            ):
                ved_design = ved
            elif (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() != 0
                or self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() != 0
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
                foundation_moments = abs(
                    column_ult_moment_Xdir + column_ult_moment_Ydir
                )
                if self.beta == 1:
                    beta = 1 + (
                        k
                        * (foundation_moments / design_punching_shear_force_eff)
                        * (perimeter_length / W)
                    )
                elif self.beta != 1:
                    beta = self.beta
                ved_design = ved * beta
            if self.__punching_shear()[2] > ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2\
                    exceeds the design punching shear stress of {round(area,3)}N/mm\u00b2 - PASS!!!"
            elif self.__punching_shear()[2] < ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2\
                    is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"

    def col_1_punching_shear_check_2d(self):
        """
        Calculates the punching shear at a distance 2d from the column one face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        average_depth = 2 * np.average([self.dy, self.dx])
        if (average_depth > self.CombinedFootingAnalysis.column_1_geometry[2]) or (
            average_depth > self.CombinedFootingAnalysis.column_1_geometry[3]
        ):
            return None
        elif (average_depth < self.CombinedFootingAnalysis.column_1_geometry[2]) or (
            average_depth < self.CombinedFootingAnalysis.column_1_geometry[3]
        ):
            cx = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[1]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[0]
            ) / self.CombinedFootingAnalysis.foundation_length
            cy = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[0]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[1]
            ) / self.CombinedFootingAnalysis.foundation_width
            c1 = self.CombinedFootingAnalysis.column_1_geometry[0]
            c2 = self.CombinedFootingAnalysis.column_1_geometry[1]
            soil_pressure_ult1 = self.CombinedFootingAnalysis.pad_base_pressures_uls()[
                0
            ]
            eccxa = (
                self.CombinedFootingAnalysis.column_1_geometry[2]
                - self.CombinedFootingAnalysis.foundation_length / 2
            )
            eccya = (
                self.CombinedFootingAnalysis.column_1_geometry[3]
                - self.CombinedFootingAnalysis.foundation_width / 2
            )
            ult_pressure_punching_shear = (
                soil_pressure_ult1
                + (
                    (
                        self.CombinedFootingAnalysis.foundation_length / 2
                        + eccxa
                        - self.CombinedFootingAnalysis.column_1_geometry[0] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_length
                        + 2 * average_depth
                    )
                )
                * cx
                / self.CombinedFootingAnalysis.foundation_width
                - (
                    (
                        self.CombinedFootingAnalysis.foundation_width / 2
                        + eccya
                        - self.CombinedFootingAnalysis.column_1_geometry[1] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_width
                        + 2 * average_depth
                    )
                )
                * cy
                / self.CombinedFootingAnalysis.foundation_length
            )
            area = (2 * (c1 + c2) * average_depth) + (math.pi * average_depth**2)
            perimeter_length = 2 * (c1 + c2) + 2 * (math.pi * average_depth)
            fdn_loads = self.foundation_loads(
                self.CombinedFootingAnalysis.foundation_thickness * 1000,
                self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
                self.CombinedFootingAnalysis.soil_unit_weight,
                self.CombinedFootingAnalysis.concrete_unit_weight,
            )
            fdn_loads_ult = (
                1.35
                * sum(fdn_loads)
                * self.CombinedFootingAnalysis.area_of_foundation()
            )
            column_axial_load = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_axial_loads[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_axial_loads[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_axial_loads[2]
                )
            )
            design_punching_shear_force = (
                column_axial_load
                + (
                    (
                        (
                            fdn_loads_ult
                            / self.CombinedFootingAnalysis.area_of_foundation()
                        )
                        - ult_pressure_punching_shear
                    )
                )
                * area
            )
            column_ult_moment_Xdir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_xdir[2]
                )
            )
            column_ult_moment_Ydir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_1_moments_ydir[2]
                )
            )
            design_punching_shear_force_eff = design_punching_shear_force * (
                1
                + 1
                * abs(column_ult_moment_Xdir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_1_geometry[1]
                + 1
                * abs(column_ult_moment_Ydir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_1_geometry[0]
            )
            ved = (design_punching_shear_force_eff * 1000) / (
                perimeter_length * average_depth * 1000000
            )
            if (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() == 0
                and self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() == 0
            ):
                ved_design = ved
            elif (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() != 0
                or self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() != 0
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
                foundation_moments = abs(
                    column_ult_moment_Xdir + column_ult_moment_Ydir
                )
                if self.beta == 1:
                    beta = 1 + (
                        k
                        * (foundation_moments / design_punching_shear_force_eff)
                        * (perimeter_length / W)
                    )
                elif self.beta != 1:
                    beta = self.beta
                ved_design = ved * beta
            if self.__punching_shear()[1] > ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2 \
                    exceeds the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - PASS!!!"
            elif self.__punching_shear()[1] < ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2 \
            is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"

    def col_2_punching_shear_column_face(self):
        """
        Calculates the punching shear at the column two face and check for its adequacy.

        Return
        ------
        string
            Maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        column_perimeter = 2 * (
            self.CombinedFootingAnalysis.column_2_geometry[0]
            + self.CombinedFootingAnalysis.column_2_geometry[1]
        )
        design_punching_shear_force = (
            (
                self.CombinedFootingAnalysis.uls_strength_factor_permanent
                * self.CombinedFootingAnalysis.column_2_axial_loads[0]
            )
            + (
                self.CombinedFootingAnalysis.uls_strength_factor_imposed
                * self.CombinedFootingAnalysis.column_2_axial_loads[1]
            )
            + (
                self.CombinedFootingAnalysis.uls_strength_factor_imposed
                * self.CombinedFootingAnalysis.column_2_axial_loads[2]
            )
        )
        punching_shear_stress = self.beta * (
            design_punching_shear_force
            / (column_perimeter * np.average([self.dy, self.dx]) * 1000)
        )
        vrd_max = self.__punching_shear()[0]
        if vrd_max > punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 exceeds the design\
                punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - PASS!!!"
        elif vrd_max < punching_shear_stress:
            return f"The maximum punching shear resistance of {round(vrd_max,3)}N/mm\u00b2 is less than the \
                design punching shear stress of {round(punching_shear_stress,3)}N/mm\u00b2 - FAIL!!!"

    def col_2_punching_shear_check_1d(self):
        """
        Calculates the punching shear at a distance 1d from the column two face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        average_depth = np.average([self.dy, self.dx])
        if (average_depth > self.CombinedFootingAnalysis.column_2_geometry[2]) or (
            average_depth > self.CombinedFootingAnalysis.column_2_geometry[3]
        ):
            return None
        elif (average_depth < self.CombinedFootingAnalysis.column_2_geometry[2]) or (
            average_depth < self.CombinedFootingAnalysis.column_2_geometry[3]
        ):
            cx = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[1]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[0]
            ) / self.CombinedFootingAnalysis.foundation_length
            cy = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[0]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[1]
            ) / self.CombinedFootingAnalysis.foundation_width
            c1 = self.CombinedFootingAnalysis.column_2_geometry[0]
            c2 = self.CombinedFootingAnalysis.column_2_geometry[1]
            soil_pressure_ult1 = self.CombinedFootingAnalysis.pad_base_pressures_uls()[
                0
            ]
            eccxa = (
                self.CombinedFootingAnalysis.column_2_geometry[2]
                - self.CombinedFootingAnalysis.foundation_length / 2
            )
            eccya = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                - self.CombinedFootingAnalysis.foundation_width / 2
            )
            ult_pressure_punching_shear = (
                soil_pressure_ult1
                + (
                    (
                        self.CombinedFootingAnalysis.foundation_length / 2
                        + eccxa
                        - self.CombinedFootingAnalysis.column_2_geometry[0] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_length
                        + 2 * average_depth
                    )
                )
                * cx
                / self.CombinedFootingAnalysis.foundation_width
                - (
                    (
                        self.CombinedFootingAnalysis.foundation_width / 2
                        + eccya
                        - self.CombinedFootingAnalysis.column_2_geometry[1] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_width
                        + 2 * average_depth
                    )
                )
                * cy
                / self.CombinedFootingAnalysis.foundation_length
            )
            area = (2 * (c1 + c2) * average_depth) + (math.pi * average_depth**2)
            perimeter_length = 2 * (c1 + c2) + 2 * (math.pi * average_depth)
            fdn_loads = self.foundation_loads(
                self.CombinedFootingAnalysis.foundation_thickness * 1000,
                self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
                self.CombinedFootingAnalysis.soil_unit_weight,
                self.CombinedFootingAnalysis.concrete_unit_weight,
            )
            fdn_loads_ult = (
                1.35
                * sum(fdn_loads)
                * self.CombinedFootingAnalysis.area_of_foundation()
            )
            column_axial_load = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_axial_loads[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_axial_loads[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_axial_loads[2]
                )
            )
            design_punching_shear_force = (
                column_axial_load
                + (
                    (
                        (
                            fdn_loads_ult
                            / self.CombinedFootingAnalysis.area_of_foundation()
                        )
                        - ult_pressure_punching_shear
                    )
                )
                * area
            )
            column_ult_moment_Xdir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[2]
                )
            )
            column_ult_moment_Ydir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[2]
                )
            )
            design_punching_shear_force_eff = design_punching_shear_force * (
                1
                + 1
                * abs(column_ult_moment_Xdir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_2_geometry[1]
                + 1
                * abs(column_ult_moment_Ydir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_2_geometry[0]
            )
            ved = (design_punching_shear_force_eff * 1000) / (
                perimeter_length * average_depth * 1000000
            )
            if (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() == 0
                and self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() == 0
            ):
                ved_design = ved
            elif (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() != 0
                or self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() != 0
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
                foundation_moments = abs(
                    column_ult_moment_Xdir + column_ult_moment_Ydir
                )
                if self.beta == 1:
                    beta = 1 + (
                        k
                        * (foundation_moments / design_punching_shear_force_eff)
                        * (perimeter_length / W)
                    )
                elif self.beta != 1:
                    beta = self.beta
                ved_design = ved * beta
            if self.__punching_shear()[2] > ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2 \
                    exceeds the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - PASS!!!"
            elif self.__punching_shear()[2] < ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[2],3)}N/mm\u00b2 \
                    is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"

    def col_2_punching_shear_check_2d(self):
        """
        Calculates the punching shear at a distance 2d from the column two face and check for its adequacy.

        Return
        ------
        string
            maximum punching shear resistance in N/mm2 and design punching shear stress in N/mm2
        """
        average_depth = 2 * np.average([self.dy, self.dx])
        if (average_depth > self.CombinedFootingAnalysis.column_2_geometry[2]) or (
            average_depth > self.CombinedFootingAnalysis.column_2_geometry[3]
        ):
            return None
        elif (average_depth < self.CombinedFootingAnalysis.column_2_geometry[2]) or (
            average_depth < self.CombinedFootingAnalysis.column_2_geometry[3]
        ):
            cx = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[1]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_X()[0]
            ) / self.CombinedFootingAnalysis.foundation_length
            cy = (
                self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[0]
                - self.CombinedFootingAnalysis.base_pressure_rate_of_change_Y()[1]
            ) / self.CombinedFootingAnalysis.foundation_width
            c1 = self.CombinedFootingAnalysis.column_2_geometry[0]
            c2 = self.CombinedFootingAnalysis.column_2_geometry[1]
            soil_pressure_ult1 = self.CombinedFootingAnalysis.pad_base_pressures_uls()[
                0
            ]
            eccxa = (
                self.CombinedFootingAnalysis.column_2_geometry[2]
                - self.CombinedFootingAnalysis.foundation_length / 2
            )
            eccya = (
                self.CombinedFootingAnalysis.column_2_geometry[3]
                - self.CombinedFootingAnalysis.foundation_width / 2
            )
            ult_pressure_punching_shear = (
                soil_pressure_ult1
                + (
                    (
                        self.CombinedFootingAnalysis.foundation_length / 2
                        + eccxa
                        - self.CombinedFootingAnalysis.column_2_geometry[0] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_length
                        + 2 * average_depth
                    )
                )
                * cx
                / self.CombinedFootingAnalysis.foundation_width
                - (
                    (
                        self.CombinedFootingAnalysis.foundation_width / 2
                        + eccya
                        - self.CombinedFootingAnalysis.column_2_geometry[1] / 2
                        - average_depth
                    )
                    + 0.5
                    * (
                        self.CombinedFootingAnalysis.foundation_width
                        + 2 * average_depth
                    )
                )
                * cy
                / self.CombinedFootingAnalysis.foundation_length
            )
            area = (2 * (c1 + c2) * average_depth) + (math.pi * average_depth**2)
            perimeter_length = 2 * (c1 + c2) + 2 * (math.pi * average_depth)
            fdn_loads = self.foundation_loads(
                self.CombinedFootingAnalysis.foundation_thickness * 1000,
                self.CombinedFootingAnalysis.soil_depth_abv_foundation * 1000,
                self.CombinedFootingAnalysis.soil_unit_weight,
                self.CombinedFootingAnalysis.concrete_unit_weight,
            )
            fdn_loads_ult = (
                1.35
                * sum(fdn_loads)
                * self.CombinedFootingAnalysis.area_of_foundation()
            )
            column_axial_load = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_axial_loads[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_axial_loads[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_axial_loads[2]
                )
            )
            design_punching_shear_force = (
                column_axial_load
                + (
                    (
                        (
                            fdn_loads_ult
                            / self.CombinedFootingAnalysis.area_of_foundation()
                        )
                        - ult_pressure_punching_shear
                    )
                )
                * area
            )
            column_ult_moment_Xdir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_xdir[2]
                )
            )
            column_ult_moment_Ydir = (
                (
                    self.CombinedFootingAnalysis.uls_strength_factor_permanent
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[0]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[1]
                )
                + (
                    self.CombinedFootingAnalysis.uls_strength_factor_imposed
                    * self.CombinedFootingAnalysis.column_2_moments_ydir[2]
                )
            )
            design_punching_shear_force_eff = design_punching_shear_force * (
                1
                + 1
                * abs(column_ult_moment_Xdir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_2_geometry[1]
                + 1
                * abs(column_ult_moment_Ydir)
                / design_punching_shear_force
                * self.CombinedFootingAnalysis.column_2_geometry[0]
            )
            ved = (design_punching_shear_force_eff * 1000) / (
                perimeter_length * average_depth * 1000000
            )
            if (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() == 0
                and self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() == 0
            ):
                ved_design = ved
            elif (
                self.CombinedFootingAnalysis.eccentricity_X_direction_uls() != 0
                or self.CombinedFootingAnalysis.eccentricity_Y_direction_uls() != 0
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
                foundation_moments = abs(
                    column_ult_moment_Xdir + column_ult_moment_Ydir
                )
                if self.beta == 1:
                    beta = 1 + (
                        k
                        * (foundation_moments / design_punching_shear_force_eff)
                        * (perimeter_length / W)
                    )
                elif self.beta != 1:
                    beta = self.beta
                ved_design = ved * beta
            if self.__punching_shear()[1] > ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2\
                    exceeds the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - PASS!!!"
            elif self.__punching_shear()[1] < ved_design:
                return f"The maximum punching shear resistance of {round(self.__punching_shear()[1],3)}N/mm\u00b2 \
            is less than the design punching shear stress of {round(ved_design,3)}N/mm\u00b2 - FAIL!!!"
