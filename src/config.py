from dataclasses import dataclass

@dataclass(frozen=True)
class EngineCase:
    thrust: float = 100_000.0
    specific_impulse: float = 350.0
    mixture_ratio: float = 3.5
    burn_time: float = 10.0

    def __post_init__(self) -> None:
        if self.thrust <=0:
            raise ValueError("Thrust must be positive")

        if self.specific_impulse <=0:
            raise ValueError("Specific impulse must be positive.")

        if self.mixture_ratio <=0:
            raise ValueError("Mixture ratio must be positive")

        if self.burn_time <=0:
            raise ValueError("Burn time must be positive")
        
