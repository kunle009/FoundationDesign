.. _docstrings:

===========================
FoundationDesign Reference
===========================

Pad Foundation Analysis
-----------------------
.. autoclass:: FoundationDesign.PadFoundation
.. autofunction:: FoundationDesign.PadFoundation.__init__
.. autofunction:: FoundationDesign.PadFoundation.area_of_foundation
.. autofunction:: FoundationDesign.PadFoundation.plot_geometry
.. autofunction:: FoundationDesign.PadFoundation.foundation_loads
.. autofunction:: FoundationDesign.PadFoundation.column_axial_loads
.. autofunction:: FoundationDesign.PadFoundation.column_horizontal_loads_xdir
.. autofunction:: FoundationDesign.PadFoundation.column_horizontal_loads_ydir
.. autofunction:: FoundationDesign.PadFoundation.column_moments_xdir
.. autofunction:: FoundationDesign.PadFoundation.column_moments_ydir
.. autofunction:: FoundationDesign.PadFoundation.total_force_X_dir_sls
.. autofunction:: FoundationDesign.PadFoundation.total_force_Y_dir_sls
.. autofunction:: FoundationDesign.PadFoundation.total_force_Z_dir_sls
.. autofunction:: FoundationDesign.PadFoundation.total_moments_X_direction_sls
.. autofunction:: FoundationDesign.PadFoundation.total_moments_Y_direction_sls
.. autofunction:: FoundationDesign.PadFoundation.eccentricity_X_direction_sls
.. autofunction:: FoundationDesign.PadFoundation.eccentricity_Y_direction_sls
.. autofunction:: FoundationDesign.PadFoundation.pad_base_pressures_sls
.. autofunction:: FoundationDesign.PadFoundation.bearing_pressure_check_sls
.. autofunction:: FoundationDesign.PadFoundation.plot_base_pressures_sls
.. autofunction:: FoundationDesign.PadFoundation.total_force_X_dir_uls
.. autofunction:: FoundationDesign.PadFoundation.total_force_Y_dir_uls
.. autofunction:: FoundationDesign.PadFoundation.total_force_Z_dir_uls
.. autofunction:: FoundationDesign.PadFoundation.total_moments_X_direction_uls
.. autofunction:: FoundationDesign.PadFoundation.total_moments_Y_direction_uls
.. autofunction:: FoundationDesign.PadFoundation.eccentricity_X_direction_uls
.. autofunction:: FoundationDesign.PadFoundation.eccentricity_Y_direction_uls
.. autofunction:: FoundationDesign.PadFoundation.pad_base_pressures_uls
.. autofunction:: FoundationDesign.PadFoundation.base_pressure_rate_of_change_X
.. autofunction:: FoundationDesign.PadFoundation.base_pressure_rate_of_change_Y


Pad Foundation Design
---------------------
.. autoclass:: FoundationDesign.padFoundationDesign
.. autofunction:: FoundationDesign.padFoundationDesign.__init__
.. autofunction:: FoundationDesign.padFoundationDesign.__loading_diagrams_X_dir
.. autofunction:: FoundationDesign.padFoundationDesign.__loading_diagrams_Y_dir
.. autofunction:: FoundationDesign.padFoundationDesign.plot_foundation_loading_X
.. autofunction:: FoundationDesign.padFoundationDesign.plot_foundation_loading_Y
.. autofunction:: FoundationDesign.padFoundationDesign.plot_bending_moment_X
.. autofunction:: FoundationDesign.padFoundationDesign.plot_bending_moment_Y
.. autofunction:: FoundationDesign.padFoundationDesign.plot_shear_force_X
.. autofunction:: FoundationDesign.padFoundationDesign.plot_shear_force_Y
.. autofunction:: FoundationDesign.padFoundationDesign.get_design_moment_X
.. autofunction:: FoundationDesign.padFoundationDesign.get_design_moment_Y
.. autofunction:: FoundationDesign.padFoundationDesign.get_design_shear_force_X
.. autofunction:: FoundationDesign.padFoundationDesign.get_design_shear_force_Y
.. autofunction:: FoundationDesign.padFoundationDesign.area_of_steel_reqd_X_dir
.. autofunction:: FoundationDesign.padFoundationDesign.__reinforcement_calculations_X_dir
.. autofunction:: FoundationDesign.padFoundationDesign.reinforcement_provision_flexure_X_dir
.. autofunction:: FoundationDesign.padFoundationDesign.area_of_steel_reqd_Y_dir
.. autofunction:: FoundationDesign.padFoundationDesign.__reinforcement_calculations_Y_dir
.. autofunction:: FoundationDesign.padFoundationDesign.reinforcement_provision_flexure_Y_dir
.. autofunction:: FoundationDesign.padFoundationDesign.tranverse_shear_check_Xdir
.. autofunction:: FoundationDesign.padFoundationDesign.tranverse_shear_check_Ydir
.. autofunction:: FoundationDesign.padFoundationDesign.__punching_shear
.. autofunction:: FoundationDesign.padFoundationDesign.update_punching_shear_stress_factor
.. autofunction:: FoundationDesign.padFoundationDesign.punching_shear_column_face
.. autofunction:: FoundationDesign.padFoundationDesign.punching_shear_check_1d
.. autofunction:: FoundationDesign.padFoundationDesign.punching_shear_check_2d


Combined Pad Foundation Analysis
--------------------------------
.. autoclass:: FoundationDesign.CombinedFootingAnalysis
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.__init__
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_geometry
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_geometry
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_axial_loads
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_horizontal_loads_xdir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_horizontal_loads_ydir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_moments_xdir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_1_moments_ydir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_axial_loads
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_horizontal_loads_xdir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_horizontal_loads_ydir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_moments_xdir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.update_column_2_moments_ydir
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.foundation_loads
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.area_of_foundation
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_X_dir_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Y_dir_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Z_dir_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Y_dir_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Z_dir_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_moments_X_direction_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_moments_Y_direction_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.eccentricity_X_direction_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.eccentricity_Y_direction_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.pad_base_pressures_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.bearing_pressure_check_sls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.minimum_area_required_wt_moment
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.minimum_area_required
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.foundation_geometry_optimizer
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.plot_optimized_geometry
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_X_dir_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Y_dir_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Z_dir_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Y_dir_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_force_Z_dir_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_moments_X_direction_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.total_moments_Y_direction_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.eccentricity_X_direction_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.eccentricity_Y_direction_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.pad_base_pressures_uls
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.base_pressure_rate_of_change_X
.. autofunction:: FoundationDesign.CombinedFootingAnalysis.base_pressure_rate_of_change_Y

Combined Pad Foundation Design
------------------------------
.. autoclass:: FoundationDesign.CombinedFootingDesign
.. autofunction:: FoundationDesign.CombinedFootingDesign.__init__
.. autofunction:: FoundationDesign.CombinedFootingDesign.__loading_diagrams_X_dir
.. autofunction:: FoundationDesign.CombinedFootingDesign.__loading_diagrams_Y_dir
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_foundation_loading_X
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_foundation_loading_Y
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_bending_moment_X
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_bending_moment_Y
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_shear_force_X
.. autofunction:: FoundationDesign.CombinedFootingDesign.plot_shear_force_Y
.. autofunction:: FoundationDesign.CombinedFootingDesign.get_design_moment_X
.. autofunction:: FoundationDesign.CombinedFootingDesign.get_design_moment_Y
.. autofunction:: FoundationDesign.CombinedFootingDesign.get_design_shear_force_X
.. autofunction:: FoundationDesign.CombinedFootingDesign.get_design_shear_force_Y
.. autofunction:: FoundationDesign.CombinedFootingDesign.area_of_steel_reqd_X_dir
.. autofunction:: FoundationDesign.CombinedFootingDesign.area_of_steel_reqd_Y_dir
.. autofunction:: FoundationDesign.CombinedFootingDesign.tranverse_shear_check_Xdir
.. autofunction:: FoundationDesign.CombinedFootingDesign.tranverse_shear_check_Ydir
.. autofunction:: FoundationDesign.CombinedFootingDesign.__punching_shear
.. autofunction:: FoundationDesign.CombinedFootingDesign.update_punching_shear_stress_factor
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_1_punching_shear_column_face
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_1_punching_shear_check_1d
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_1_punching_shear_check_2d
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_2_punching_shear_column_face
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_2_punching_shear_check_1d
.. autofunction:: FoundationDesign.CombinedFootingDesign.col_2_punching_shear_check_2d
