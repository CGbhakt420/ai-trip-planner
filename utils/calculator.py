import ast
import math
import operator
from typing import Callable


_BINARY_OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
_UNARY_OPERATORS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}
MAX_EXPRESSION_LENGTH = 256
MAX_AST_NODES = 64
MAX_EXPONENT = 100


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        if isinstance(node.value, bool):
            raise ValueError("Boolean values are not supported.")
        if len(str(node.value)) > 100:
            raise ValueError("Numeric literals are too large.")
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPERATORS:
        return _UNARY_OPERATORS[type(node.op)](_evaluate(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPERATORS:
        left = _evaluate(node.left)
        right = _evaluate(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError(f"Exponent magnitude must not exceed {MAX_EXPONENT}.")
        result = _BINARY_OPERATORS[type(node.op)](left, right)
        if isinstance(result, complex):
            raise ValueError("Complex results are not supported.")
        return result
    raise ValueError("Only numeric literals and basic arithmetic are supported.")


def calculate(expression: str) -> int | float:
    """Safely evaluate a basic arithmetic expression."""
    if not expression.strip():
        raise ValueError("An arithmetic expression is required.")
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")
    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise ValueError("Invalid arithmetic expression.") from error
    if sum(1 for _ in ast.walk(parsed)) > MAX_AST_NODES:
        raise ValueError("Expression is too complex.")

    try:
        result = _evaluate(parsed)
    except (OverflowError, ZeroDivisionError) as error:
        raise ValueError("Expression could not be evaluated safely.") from error
    if not math.isfinite(result):
        raise ValueError("Calculation result is not finite.")
    if result.is_integer():
        return int(result)
    return result