from dataclasses import dataclass
from fractions import Fraction


@dataclass
class DataProblem:
    quant_vars: int
    quant_constr: int
    function_coefficients: list[Fraction]
    constraints: list[list[Fraction]]
    basic_vars: list[int] | None = None


@dataclass
class SimplexInput:
    table: list[list[Fraction]]
    down_row: list[dict[str, Fraction]]
    b_vars: list[int]


@dataclass
class SimplexResult:
    x_vars: list[Fraction]
    func_res: Fraction
