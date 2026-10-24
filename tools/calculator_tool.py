from langchain_core.tools import tool

from utils.calculator import calculate as evaluate_expression


@tool
def calculate(expression: str) -> dict[str, str | int | float]:
    """Safely calculate an arithmetic expression for trip budgets and cost totals."""
    return {"expression": expression, "result": evaluate_expression(expression)}