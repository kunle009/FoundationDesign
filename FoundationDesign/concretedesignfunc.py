import math
from scipy.interpolate import interp1d
import numpy as np


def shear_check_column_face(column_perimeter: float, fck: float, d: float):
    """
    Function to check the shear at column face. This would be used to ascertain
    the suitability of the initial depth assumed.

    Parameters
    ----------
    column_perimeter : float
        The column perimeter in m
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
    fyk : float
        Characteristic yield strength of reinforcement in N/mm2
    d : float
        Depth to tension reinforcement in mm

    Returns
    -------
    float
        Maximum shear resistance in N/mm2
    """
    Vrd_max = (0.5 * column_perimeter * d * (0.6 * (1 - fck / 250)) * fck / 1.5) / 1000
    return Vrd_max


def punching_shear_column_face(d, fck, column_perimeter):
    """
    Function to check the shear at column face.

    Parameters
    ----------
    column_perimeter : float
        The column perimeter in m
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
    d : float
        Depth to tension reinforcement in mm
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]

    Returns
    -------
    float
        Maximum shear resistance in N/mm2
    """
    vrd_max = 0.2 * (1 - fck / 250) * fck * column_perimeter * d
    return round(vrd_max, 3)


def bending_reinforcement(m, depth, fck, fyk, length):
    """
    Function to calculate the area of steel required according to eurocode 2.

    Parameters
    ----------
    m : float
        design bending moment in kNm
    depth : float
        Depth to tension reinforcement in m
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
    fyk : float
        Characteristic yield strength of reinforcement in N/mm2
    length : float
        Length of the element to be designed in mm

    Returns
    -------
    float
        Area of steel required in mm2
    """
    depth = depth * 1000
    k = (m * 10**6) / (fck * length * (depth**2.0))
    if k > 0.167:
        print("Compression Reinforcement required, design out of scope")
    la = 0.5 + math.sqrt(0.25 - (0.882 * k))
    if la >= 0.95:
        la = 0.95
    area_of_steel = (m * 10**6) / (0.87 * fyk * la * depth)
    return round(area_of_steel, 0)


def minimum_steel(fck, fyk, bt, d):
    """
    Function to calculate the minimum area of steel required.

    Parameters
    ----------
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]
    fyk : float
        Characteristic yield strength of reinforcement in N/mm2
    bt : float
        width in mm
    d : float
        Depth to tension reinforcement in m

    Returns
    -------
    float
        Minimum area of steel required in mm2
    """
    d = d * 1000
    as_min = (0.078 * (fck ** (2 / 3)) / fyk) * bt * d
    limiting_as = 0.0013 * bt * d
    minimum_as = max(as_min, limiting_as)
    return round(minimum_as, 0)


def maximum_steel(length, d):
    """
    Function to calculate the maximum area of steel required.

    Parameters
    ----------
    length : float
        Length in m
    d : float
        Depth to tension reinforcement in m

    Returns
    -------
    float
        Maximum area of steel required in mm2
    """
    max_area = 0.04 * length * d
    return max_area


def shear_stress_check_1d(d, px, fck):
    """
    Function to determine the rectangular section in shear at a distance equivalent to 1d from the column face.

    Parameters
    ----------
    d : float
        Depth to tension reinforcement in m
    px : float
        Longitudinal reinforcement ratio unitless
    fck : float
        Characteristic compressive cylinder strength in N/mm2. Accepted range of values [16,20,25,30,32,35,37,40,45,55]

    Returns
    -------
    float
        resistance of members without shear reinforcement in MPa
    """
    k = min((1 + math.sqrt(200 / d)), 2)
    p1 = min(px, 0.02)
    vrd_c = max(
        (0.12 * k * ((100 * p1 * fck) ** (1 / 3))), (0.035 * (k**1.5) * (fck**0.5))
    )
    return round(vrd_c, 3)


def column_punching_coefficient_k(column_ratio):
    """Interpolating Values of k for rectangular loaded areas from table 6.1 of the Eurocode 2."""
    x = np.array([0.5, 1, 2, 3])
    y = np.array([0.45, 0.6, 0.7, 0.8])
    if column_ratio < np.min(x) or column_ratio > np.max(x):
        raise ValueError("column_ratio is outside the valid range for interpolation")
    # Linear interpolation using numpy.interp
    k = np.interp(column_ratio, x, y)
    return k


def reinforcement_provision(assteel, fy):
    """
    Reinforcement area (mm2/m) for different bar spacing.

    Parameters
    ----------
    assteel : float
        Area of steel required calculated in mm2/m
    fy : float
        Characteristic yield strength of reinforcement in N/mm2

    Returns
    -------
    t : string
        Steel class label R for mild steel Grade 250, Y for Grade 410 (Type 2), T for Grade 460 (Type 2),
         H for Grade 500 (Type 2).
    rd : string
        Rod diameters in mm range 8,10,12,16,20,25,32,40
    sv : float
        bar spacing in mm
    asteel_provided : float
        Area of steel provided in mm2/m
    """
    if fy <= 250:
        t = "R"
    elif fy > 250 and fy <= 410:
        t = "Y"
    elif fy > 410 and fy <= 460:
        t = "T"
    elif fy > 460 and fy <= 500:
        t = "H"
    if assteel <= 402:
        rd = "8mm"
        dia = 8.00
    elif assteel > 402 and assteel <= 628:
        rd = "10mm"
        dia = 10.00
    elif assteel > 628 and assteel <= 905:
        rd = "12mm"
        dia = 12.00
    elif assteel > 905 and assteel <= 1610:
        rd = "16mm"
        dia = 16.00
    elif assteel > 1610 and assteel <= 2510:
        rd = "20mm"
        dia = 20.00
    elif assteel > 2510 and assteel <= 3930:
        rd = "25mm"
        dia = 25.00
    elif assteel > 3930 and assteel <= 6430:
        rd = "32mm"
        dia = 32.00
    elif assteel > 6430:
        rd = "40mm"
        dia = 40.00
    area = (math.pi * dia**2) / 4
    v1 = assteel / area
    v = 1000 / v1
    n = int(v / 25) * 25
    if n > 200 and fy <= 250:
        n = 200
    elif n > 250 and fy > 250:
        n = 250
    sv = float(n)
    asteel_provided = round(area * (1000 / sv))
    return [t, rd, sv, asteel_provided]
