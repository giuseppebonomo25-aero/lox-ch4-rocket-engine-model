from src.performance import(
    calculate_total_mass_flow,
    split_propellant_mass_flow,
)




thrust = 100_000.0
specific_impulse = 350.0
oxidizer_to_fuel_ratio = 3.5


total_flow = calculate_total_mass_flow(
    thrust=thrust,
    specific_impulse=specific_impulse,
)


lox_flow, methane_flow = split_propellant_mass_flow(
    total_mass_flow=total_flow,
    oxidizer_to_fuel_ratio=oxidizer_to_fuel_ratio,
)

print(f"Total propellant flow: {total_flow:.3f} kg/s")
print(f"LOX mass flow: {lox_flow:.3f} kg/s")
print(f"CH4 mass flow: {methane_flow: .3f} kg/s")
print(f"Mass-flow check: {lox_flow + methane_flow: .3f} kg/s")
