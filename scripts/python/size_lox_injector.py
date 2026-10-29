from math import exp, pi, sqrt

# Baseline performance targets.
thrust_N = 100000.0
isp_s  =350.0
g0_m_s2 = 9.80665
of_ratio = 3.5


total_flow_kg_s = thrust_N / (isp_s * g0_m_s2)
lox_flow_kg_s = total_flow_kg_s * of_ratio / (1.0 + of_ratio)

# Preliminary assumptions, not valitated design values.
chamber_pressure_Pa = 5.0e6
injector_pressure_drop_Pa = 1.0e6
discharge_coefficient = 0.64


# Normal-boiling-point density used as a costant approximation.
# Same constant-bulk-modulus approximation as the Simscape model.
reference_pressure_Pa = 101325.0
reference_density_kg_m3 = 1142.108492
bulk_modulus_Pa = 5.12866481e8

inlet_pressure_for_properties_Pa = (
    chamber_pressure_Pa + injector_pressure_drop_Pa
)

outlet_density_kg_m3 = reference_density_kg_m3 * exp(
    (chamber_pressure_Pa - reference_pressure_Pa) / bulk_modulus_Pa
)

inlet_density_kg_m3 = reference_density_kg_m3 * exp(
    (inlet_pressure_for_properties_Pa - reference_pressure_Pa)
    / bulk_modulus_Pa
)

lox_density_kg_m3 = (
    inlet_density_kg_m3 + outlet_density_kg_m3
) / 2.0

assert injector_pressure_drop_Pa > 0
assert 0 < discharge_coefficient <= 1
assert lox_density_kg_m3 > 0

inlet_pressure_Pa = (
    chamber_pressure_Pa + injector_pressure_drop_Pa
)

equivalent_area_m2 = lox_flow_kg_s / ( 
    discharge_coefficient
    * sqrt(2.0 * lox_density_kg_m3 * injector_pressure_drop_Pa)
    )

equivalent_diameter_m = sqrt(4.0 * equivalent_area_m2 / pi)

print("---Preliminary LOX injector sizing---")
print(f"Target LOX flow: {lox_flow_kg_s:.6f} kg/s")
print(f"Chamber pressure: {chamber_pressure_Pa / 1e5:.2f} bar")
print(f"Injector inlet pressure: {inlet_pressure_Pa / 1e5:.2f} bar")
print(f"Injector pressure drop: {injector_pressure_drop_Pa / 1e5:.2f} bar")
print(
    "Pressure-drop ratio: "
    f"{injector_pressure_drop_Pa / chamber_pressure_Pa: .3f}"
)
print(f"Assumed discharge coefficient: {discharge_coefficient:.3f}")
print(f"Mean operating LOX density: {lox_density_kg_m3:.1f} kg/m^3")
print(f"Equivalent area: {equivalent_area_m2:.8e} m^2")
print(f"Equivalent area: {equivalent_area_m2 * 1e6:.3f} mm^2")
print(f"Equivalent circular diameter: {equivalent_diameter_m * 1e3:.3f} mm")
