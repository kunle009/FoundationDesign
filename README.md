
# FoundationDesign

[![PyPi](https://img.shields.io/pypi/v/FoundationDesign.svg)](https://pypi.org/project/FoundationDesign/)
![PyPI - License](https://img.shields.io/pypi/l/FoundationDesign)

FoundationDesign is a python module to be used for the design and analysis
of different foundation types in accordance to the Eurocode 2.
This project is an attempt to have a free standalone python package that can
be used to analyse and design foundations with results as good as paid softwares.
This module will be useful in determining:

- The critical bending moments in the foundation
- Critical shear force in the foundation
- Transverse shear check of the foundation
- Sliding checks
- Crack width checks
- Reinforcement provisions
- Punching shear checks etc

The project is based mainly on instructions contained in the Eurocode 2
alongside python packages like numpy,plotly,scipy and IndeterminateBeam package. Comprehensive
examples are contained in the examples folder

## Project Purpose

1. Create a free python package that can analyse and design pad foundation,combined footing foundation,
    pile foundation and/or raft foundation design.

2. Create the web version of this module.

## Functionality and usage

For now this package is limited to only concentric and eccentric pad foundation and combined footing foundation types.
A typical use case of the pad foundation class contained in the ```FoundationDesign``` module includes

- Create a `PadFoundation` object to help analyse
- Assign `foundation_loads` to the `PadFoundation`
- Assign `column_axial_loads` to the `PadFoundation`
- Assign `column_horizontal_loads_xdir` to the `PadFoundation`
- Assign `column_horizontal_loads_xdir` to the `PadFoundation`
- Assign `column_moments_xdir` to the `PadFoundation`
- Assign `column_moments_ydir` to the `PadFoundation`
- Check the `minimum_area_required` for the `PadFoundation`
- Check the `bearing_pressure_check_sls` on the `PadFoundation`
- Create a `PadFoundationDesign` object to help design the foundation
- Plot the Bending moment and shear force diagrams
- Check the area of steel required and provided in x and y direction
- Check the adequacy of the transverse shear along both column_axial_loads
- Check for `punching_shear_column_face` on the `PadFoundationDesign` object
- Check for `punching_shear_check_1d` on the `PadFoundationDesign` object
- Check for `punching_shear_check_2d` on the `PadFoundationDesign` object

## Creating a Pad Foundation

The creation of a `PadFoundation` instance involves the input of the following:

1. Foundation Length in mm
2. Foundation Width in mm
3. Column Length in mm
4. Column Width in mm
5. The position of the column along x direction from the origin in mm
6. The position of the column along y direction from the origin in mm
7. The soil bearing capacity in kN/mm2

        from foundationdesign import PadFoundation,padFoundationDesign
        fdn = PadFoundation(foundation_length=2500,foundation_width=2500,column_length=400,column_width=400,col_pos_xdir=1250,col_pos_ydir=1250,soil_bearing_capacity=200)

## Assigning Foundation Loads

Soil self weight and concrete self weight can be added to the Foundation by specifying the Foundation thickness in
mm and the soil depth above the Foundation in mm. A default value of 18kN/mm&#x00B3; and 24kN/mm&#x00B3; has been specified
for soil unit weight and concrete unit weight respectively

    fdn.foundation_loads(foundation_thickness=650,soil_depth_abv_foundation=0,soil_unit_weight=18,concrete_unit_weight=24)

## Assigning Column Loads

Axial loads, horizontal loads in x and y direction, moments in x and y direction
can all be added to the pad foundation for permanent,imposed and wind load cases.

    fdn.column_axial_loads(permanent_axial_load=800,imposed_axial_load=300)

## Designing a pad foundation

To design the foundation the ```PadFoundation``` must first be created as done above
this would then be included when creating the ```padFoundationDesign``` object
The creation of this object includes the following:

1. PadFoundation object created
2. Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
3. Characteristic yield strength of reinforcement in N/mm2
4. Nominal cover to foundation in mm
5. Initial assumed bar diameter of the foundation in the x direction in mm. Accepted range of values [8,10,12,16,20,25,32,40]
   used to calculate depth to tension reinforcement along the x direction
6. Initial assumed bar diameter of the foundation in the y direction in mm Accepted range of values [8,10,12,16,20,25,32,40]
    used to calculate depth to tension reinforcement along the y direction

        fdn_design = padFoundationDesign(fdn, fck=30, fyk=500, concrete_cover=40, bar_diameterX=16, bar_diameterY=16)

## Plotting Foundation forces

Lots of checks can be done on the Foundation which can be found in the notebooks contained in the examples folder
To show the bending moment of the Foundation. The ```plot_bending_moment_X()``` can be called this figure will show the
bending moment values at the critical location along the Foundation length or width. Plotting methods takes a show_plot argument which can either be True or False. which by default is True

    fdn_design.plot_bending_moment_X()
    fdn_design.plot_shear_force_X()
This outputs the bending moment plot with the design bending moment shown at the face of the column
![Image](https://github.com/CodedKunz/FoundationDesign/blob/main/examples/bending_moment1.png?raw=true)
The shear force plot is also displayed with critical shearforce showing at 1d from column the face
![Image](https://github.com/CodedKunz/FoundationDesign/blob/main/examples/shear_force.jpg?raw=true)

## Installing the package

If you want to install the `FoundationDesign` package, you run this one-liner:

    pip install FoundationDesign

**NOTE**: You need Python 3 to install this package (you may need to write `pip3` instead of `pip`).

The library dependencies are listed in the file `requirements.txt`, but you only need to look at them if you clone the repository.
If you install the package via `pip`, the listed dependencies should be installed automatically.

## Future Works

The following are areas that will be implemented in future:

- Adding a method to calculate crack width
- PDF report generation
- User documentation
