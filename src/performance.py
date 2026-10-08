from .costants import G0

def calculate_total_mass_flow(
        thrust: float,
        specific_impulse: float,
) -> float:
    """Calculate total propellant mass flow rate."""

    if thrust <= 0:
        raise ValueError("Thrust must be positive.")

    if specific_impulse <=0:
        raise ValueError("Specific impulse must be positive")

    return thrust / (specific_impulse * G0)

def split_propellant_mass_flow(
        total_mass_flow: float,
        oxidizer_to_fuel_ratio: float,
) -> tuple[float, float]:
    """Split total mass flow into oxidizer and fuel mass flow."""

    if total_mass_flow <=0:
        raise ValueError("Total mass flow must be positive.")

    if oxidizer_to_fuel_ratio <=0:
        raise ValueError("Oxidizer-to-fuel ratio must be positive.")

    oxidizer_flow = (
        total_mass_flow
        * oxidizer_to_fuel_ratio
        /(1+ oxidizer_to_fuel_ratio)
    )

    fuel_flow = total_mass_flow / (1+oxidizer_to_fuel_ratio)

    return oxidizer_flow, fuel_flow

def check_mass_flow_balance(
    total_mass_flow: float,
    oxidiser_flow: float,
    fuel_flow: float,
    tolerance: float = 1e-10,
) -> bool:
    """Check conservation of total propellant mass flow."""

    calculated_total = oxidiser_flow + fuel_flow

    return abs(calculated_total - total_mass_flow) <= tolerance 


def calculate_propellant_mass(
    total_mass_flow: float,
    burn_time: float,
) -> float:
    """Calculate total propellant mass consumed during the burn."""

    if total_mass_flow <= 0:
        raise ValueError("Total mass flow must be positive.")

    if burn_time <= 0:
        raise ValueError("Burn time must be positive.")

    return total_mass_flow * burn_time