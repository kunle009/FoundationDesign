---
title: "FoundationDesign: A Python module for structural analysis and design of different foundation type in accordance to the Eurocodes and the UK National Annex"
tags:
  - foundation design
  - foundation analysis
  - foundation engineering
  - eurocode
  - structural engineering
  - civil engineering
  - Python
authors:
  - name: Kunle Yusuf
    orcid: 0009-0009-2339-267X
    affiliation: 1
affiliations:
  - name: No affiliation
    index: 1
date: 03 July 2025
bibliography: paper.bib
nocite: |
  @Bonanno2021, @harris2020array
---

# Summary

`FoundationDesign` is a Python module to be used for the design and analysis of different foundation types in accordance to the Eurocode 2.This project is an attempt to have a free standalone Python package that can
be used to analyse and design foundations with results as good as paid software's. This module will be useful in determining:

- The critical bending moments in the foundation
- Critical shear force in the foundation
- Transverse shear check of the foundation
- Sliding checks
- Crack width checks
- Reinforcement provisions
- Punching shear checks etc

The project is based mainly on instructions contained in the `[@en1992]` and common engineering textbooks such as `[@arya2000design]`, `[@bhatt2014reinforced]` and `[@mosley1982reinforced]`

The package can be used by:

- structural engineers to design foundations
- civil engineering students to learn the manual design of foundations

The [FoundationDesign repository](https://github.com/kunle009/) can be found on Github and is ready for installation using `pip`. Text-based examples of the package presented in the [documentation](http://foundationdesign.readthedocs.io/en/latest/examples.html) includes [Concentric Pad Foundation](https://colab.research.google.com/github/kunle009/FoundationDesign/blob/main/examples/Concentric_Footing_Example.ipynb), [Eccentric Pad Foundation](https://colab.research.google.com/github/kunle009/FoundationDesign/blob/main/examples/Eccentric_Footing_Example.ipynb) and a [Combined Footing Pad Foundation](https://colab.research.google.com/github/kunle009/FoundationDesign/blob/main/examples/Combined_Footing_Mosley_bungey.ipynb). A web-based graphical user interface (GUI) is available at [FoundationCalcs](https://foundationcalcs.com).

# Statement of Need

The structural design of foundations is a critical step in any civil infrastructure project, and proficiency in this area is essential for civil and structural engineers. However, there's a notable lack of tools that simplify and automate this process, especially via the web, which could significantly enhance accessibility to effective foundation design. The Python ecosystem for civil and structural engineers is also rapidly maturing. The `FoundationDesign` Python library contributes to this growth by complementing existing analysis and design libraries, all while remaining open source for further customization.

**FoundationDesign** is a Python package that addresses these gaps by offering:

1. **Comprehensive Theoretical Implementation**  
   The package features a clear implementation of Eurocode 2 and UK National Annex principles and guidelines regarding bending, shear, punching shear, and sliding checks.

2. **Interactive Computational Feedback**  
   Users can define foundation geometry and loads -including axial, horizontal, and moment loads—and immediately generate bending moment and shear force diagrams, base pressure and minimum-area checks, punching shear assessments, sliding stability, and reinforcement sizing. This instant visual feedback reinforces understanding through experimentation.

3. **Open-Source and Extensible**  
   In stark contrast to prevailing practices in civil engineering software development -where applications are often closed-source and operate as 'black boxes'- `FoundationDesign` represents a significant departure. By fully embracing open source and currently licensed under GPL-3.0, it encourages both academic and professional users and engineers to inspect, adapt, and extend the library. Currently, `FoundationDesign` supports the design of concentric and eccentric pad foundations, as well as combined pad foundations.

4. **Cloud Based Web GUI**  
   A companion web app [FoundationCalcs](https://foundationcalcs.com) -currently in beta- offers a GUI for the use of non programmers making the library further accessible to a wide range of users.

My structural design internship during my undergraduate studies served as the primary inspiration for this package. I spent that time designing foundations with an old Fortran command-line software that, while remarkably fast and efficient, demanded manual input through a cumbersome text file and lacked any visual feedback. This experience, alongside my growing interest in computer science since high school, propelled me to develop a more user-friendly and interactive software capable of designing foundations in a similar, powerful manner to the Fortran tool, but with a modern approach.

## Functionality and Usage

For now this package is limited to only concentric and eccentric pad foundation and combined footing foundation types.
A typical use case of the pad foundation class contained in the `FoundationDesign` module includes

- Create a `PadFoundation` object to help analyse
- Assign `Loads` to the `PadFoundation` object
- Solving for foundation forces
- Design the foundation using the `padFoundationDesign` class
- Check the design results
- Plot foundation design forces.

You can follow along with the example below, which is an excerpt from [@bhatt2014reinforced] section 11.4.2.1 page 443, in this web-based [Concentric Pad Foundation Notebook](https://colab.research.google.com/github/kunle009/FoundationDesign/blob/main/examples/Concentric_Footing_Example.ipynb).

The units used throughout the Python package are SI units (newtons and metres)

### Creating a Pad Foundation

The creation of a `PadFoundation` instance involves the input of the foundation length and breadth (m), the column length and breadth (m), soil bearing capacity (kN/m2) and the column position in the x and y direction relative to the foundation's origin (m). The `PadFoundation` class is contained in the `FoundationDesign` module and can be imported as follows:

```Python
from FoundationDesign import PadFoundation,padFoundationDesign
# Create a foundation with an initial size of 2.5m by 2.5m, supporting a 400mm x 400mm column carrying a dead load of 800kN and imposed load of 300kN
# The soil bearing capacity is 200kN/m2.
fdn = PadFoundation(
    foundation_length=2500,
    foundation_width=2500,
    column_length=400,
    column_width=400,
    col_pos_xdir=1250,
    col_pos_ydir=1250,
    soil_bearing_capacity=200,
)
```

### Defining Loads

Different types of loads are supported by `FoundationDesign` including `column_axial_loads`, `column_horizontal_loads_xdir`, `column_horizontal_loads_xdir`, `column_moments_xdir` and `column_moments_ydir.
These loads can be defined under three load cases `permanent`, `imposed`and`wind`. With their accurate sign convention contained in the [documentation](https://foundationdesign.readthedocs.io/en/latest/docstrings.html)

```Python
# Define the column axial loads with dead load of 800kN and imposed load of 300kN
fdn.column_axial_loads(permanent_axial_load=800,imposed_axial_load=300)
```

### Solving for Foundation Forces

Once the `PadFoundation` object has been assigned with `Loads` objects it can then be solved. The foundation's pressure relative to the soil bearing capacity and the minimum area of the foundation can be accessed

```Python
fdn.bearing_pressure_check_sls()['status']
area = fdn.minimum_area_required()
```

### Designing the Pad Foundation

Designing the foundation involves creating a `padFoundationDesign` object, which takes the `PadFoundation` object as an argument alongside the concrete's `Fck`, `Fy`, `concrete_cover` and the reinforcement diameter in x and y directions `bar_diameterX` and `bar_diameterY`. The design allows the user check for bending moments, shear forces, punching shear, and reinforcement requirements in both directions. A proper description of symbols and units can be found in the [documentation](https://foundationdesign.readthedocs.io/en/latest/docstrings.html).

```Python
# Design the pad foundation with a grade 30 concrete strength, reinforcement strength of 500 N/mm2, 40mm concrete cover
# and bar diameter of 16mm in both directions
fdn_design = padFoundationDesign(
    fdn, fck=30, fyk=500, concrete_cover=40, bar_diameterX=16, bar_diameterY=16
)
```

### Checking Design Results

Different results can be checked from the `padFoundationDesign` object, including the reinforcement area required and provided in both x and y directions, the transverse shear check, punching shear checks and sliding resistance check. For Example,

```Python
#Show the reinforcement area required along the x axis
fdn_design.area_of_steel_reqd_X_dir()['area_required_per_m']
# Show the transverse shear check along the x axis
fdn_design.transverse_shear_check_X_dir()['status']
# Show the punching shear check along the column face
fdn_design.punching_shear_column_face()['status']
# Show the punching shear check along the 1D perimeter
fdn_design.punching_shear_check_1d()['status']
# Show the punching shear check along the 2D perimeter
fdn_design.punching_shear_check_2d()['status']
# show the resistance of the foundation to sliding
fdn_design.sliding_resistance_check()['status']
```

### Plotting results

Lot's of results can be investigated by plotting different results from the `PadFoundation` and `padFoundationDesign` objects. The plots are generated using the `[@plotly]` library. Various other plots can be generated to visualise the foundation geometry, base pressures, loading diagrams, bending moment diagrams, and shear force diagrams. The following code snippet demonstrates how to generate some of these plots:

```Python
# Plot the bending moment diagram in x direction
fdn_design.plot_bending_moment_X()
# Plot the shear force diagram in x direction
fdn_design.plot_shear_force_X()
```

This outputs the bending moment plot with the design bending moment shown at the face of the column
![Foundation Bending Moment in X direction](https://github.com/kunle009/FoundationDesign/blob/main/assets/bending_moment1.png?raw=true)
The shear force plot is also displayed with critical shear force showing at 1d from column the face
![Foundation Shear Force in X direction](https://github.com/kunle009/FoundationDesign/blob/main/assets/shear_force.jpg?raw=true)

# References
