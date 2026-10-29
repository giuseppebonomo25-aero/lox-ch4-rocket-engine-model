import CoolProp
from CoolProp.CoolProp import PhaseSI, PropsSI

fluid = "Oxygen"

# Preliminary temperature assumption for the isothermal model.
temperature_K = 90.0

# Reference state and injector opreating pressures.
reference_pressure_Pa = 101325.0
outlet_pressure_Pa = 5.0e6
inlet_pressure_Pa = 6.0e6

states = {
    "reference": reference_pressure_Pa,
    "injector_outlet": outlet_pressure_Pa,
    "injector_inlet": inlet_pressure_Pa,
}

print(f"CoolProp version: {CoolProp.__version__}")
print(f"Fluid: {fluid}")
print(f"Assumed temperature: {temperature_K:.2f} K")


for name, pressure_Pa in states.items():
    density = PropsSI(
        "Dmass", "T", temperature_K, "P", pressure_Pa, fluid
    )
    dynamic_viscosity = PropsSI(
        "VISCOSITY", "T", temperature_K, "P", pressure_Pa, fluid
    )
    compressibility = PropsSI(
        "ISOTHERMAL_COMPRESSIBILITY", "T", temperature_K, "P", pressure_Pa, fluid,
    )


    kinematic_viscosity = dynamic_viscosity / density
    bulk_modulus = 1.0 / compressibility
    phase = PhaseSI("T", temperature_K, "P", pressure_Pa, fluid)


    print(f"\n--- {name} ---")
    print(f"Pressure: {pressure_Pa / 1e5:.5f} bar absolute")
    print(f"Phase: {phase}")
    print(f"Density: {density:.6f} kg/m^3")
    print(f"Dynamic viscosity: {dynamic_viscosity:.8e} Pa s")
    print(f"Kinematic viscosity: {kinematic_viscosity:.8e} m^2/s")
    print(f"Isothermal bulk modulus: {bulk_modulus:.8e} Pa")