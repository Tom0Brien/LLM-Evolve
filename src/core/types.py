from dataclasses import dataclass

@dataclass
class Individual:
    code: str
    fitness: float = 0.0
    feedback: str = ""
