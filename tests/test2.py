from FoundationDesign import CombinedFootingAnalysis

comb_footing = CombinedFootingAnalysis(
    foundation_length=4600,
    foundation_width=2300,
    soil_bearing_capacity=300,
    spacing_btwn_columns=3000,
)
comb_footing.update_column_1_geometry(
    column_length=300, column_width=300, col_pos_xdir=540, col_pos_ydir=1145
)
comb_footing.update_column_2_geometry(
    column_length=400, column_width=400, col_pos_xdir=3540, col_pos_ydir=1145
)
comb_footing.update_column_1_axial_loads(
    permanent_axial_load=1000, imposed_axial_load=200
)
comb_footing.update_column_2_axial_loads(
    permanent_axial_load=1400, imposed_axial_load=300
)
comb_footing.foundation_loads(
    foundation_thickness=850,
    soil_depth_abv_foundation=0,
    soil_unit_weight=18,
    concrete_unit_weight=24,
    consider_self_weight=False,
)
# min_area = comb_footing.minimum_area_required()
# z = comb_footing.foundation_geometry_optimizer()
comb_footing.plot_geometry()
pres = comb_footing.pad_base_pressures_sls()
print(pres)
pres = comb_footing.pad_base_pressures_uls()
print(pres)
comb_footing.bearing_pressure_check_sls()
comb_footing.total_axial_force_uls()
