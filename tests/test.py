from FoundationDesign import padFoundationDesign, PadFoundation

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

# outputs
# print(fdn.area_of_foundation())
# print(fdn.total_force_X_dir_sls())
# print(fdn.total_force_Y_dir_sls())
# print(fdn.total_force_Z_dir_sls())
#print(fdn.total_moments_X_direction_sls())
#print(fdn.total_moments_Y_direction_sls())
#print(fdn.eccentricity_X_direction_sls())
#print(fdn.eccentricity_Y_direction_sls())
print(fdn.pad_base_pressures_sls())
print(fdn.pad_base_pressures_uls())
#print(fdn.total_force_X_dir_uls())
#print(fdn.total_force_Y_dir_uls())
#print(fdn.total_force_Z_dir_uls())
#print(fdn.total_moments_X_direction_uls())
#print(fdn.total_moments_Y_direction_uls())
#print(fdn.eccentricity_X_direction_uls())
#print(fdn.eccentricity_Y_direction_uls())
