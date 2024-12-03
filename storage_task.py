from dataclasses import dataclass
from fractions import Fraction


@dataclass
class DataProblem:
    quant_vars: int
    quant_constr: int
    function_coefficients: list[list[Fraction]]
    constraints: list[list[Fraction]]
    basic_vars: list[int] | None = None
