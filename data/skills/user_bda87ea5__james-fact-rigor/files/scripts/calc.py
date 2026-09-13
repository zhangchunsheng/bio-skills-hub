#!/usr/bin/env python3
"""
Safe numerical computation utility for fact-rigor skill.
Use instead of mental arithmetic for any calculation in output.

Usage:
    python3 scripts/calc.py "expression"
    python3 scripts/calc.py --file calculations.txt

Examples:
    python3 scripts/calc.py "0.15 * 1200"
    python3 scripts/calc.py "(500/600)*0.105 + (100/600)*0.05*(1-0.21)"
    python3 scripts/calc.py "1000 * (1 + 0.08)**5"

The script evaluates the expression safely (no imports, no builtins beyond
math functions) and prints the result with full precision.
"""

import sys
import math
import re
import json

SAFE_MATH = {
    "abs": abs, "round": round, "min": min, "max": max,
    "sqrt": math.sqrt, "log": math.log, "log10": math.log10, "log2": math.log2,
    "exp": math.exp, "pow": pow,
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "ceil": math.ceil, "floor": math.floor,
    "pi": math.pi, "e": math.e, "tau": math.tau,
}


def safe_eval(expr: str) -> float:
    """Evaluate a mathematical expression with only safe functions."""
    # Basic sanitization: forbid dangerous patterns
    forbidden = re.compile(r"(__|import|exec|eval|compile|open|getattr|setattr|delattr|"
                           r"globals|locals|vars|dir|type|class|def|lambda|print|"
                           r"os\.|sys\.|subprocess|shutil|pathlib)")
    if forbidden.search(expr):
        raise ValueError(f"Forbidden pattern in expression: {expr}")

    # Only allow numbers, operators, parentheses, commas, dots, underscores (in numbers),
    # and known function names / constants
    allowed = re.compile(r"^[\d\s+\-*/().,%<>=!&|^~a-zA-Z_]+$")
    if not allowed.match(expr):
        raise ValueError(f"Disallowed characters in expression: {expr}")

    # Replace ^ with ** for exponentiation
    expr = expr.replace("^", "**")

    try:
        result = eval(expr, {"__builtins__": {}}, SAFE_MATH)
    except Exception as ex:
        raise ValueError(f"Failed to evaluate '{expr}': {ex}")

    return result


def format_result(value):
    """Format result for display."""
    if isinstance(value, (int, float)):
        if isinstance(value, float):
            # Show up to 10 significant digits but trim trailing zeros
            formatted = f"{value:.10g}"
            return formatted
        return str(value)
    return str(value)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 calc.py 'expression' [expression2 ...]")
        print("       python3 calc.py --json 'expression'")
        print("       python3 calc.py --file calculations.txt")
        sys.exit(1)

    if sys.argv[1] == "--file":
        if len(sys.argv) < 3:
            print("Error: --file requires a filename argument")
            sys.exit(1)
        filepath = sys.argv[2]
        with open(filepath) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        for line in lines:
            # Support "label = expression" format
            if "=" in line and not any(op in line.split("=")[0] for op in ["==", "!=", "<=", ">="]):
                parts = line.split("=", 1)
                label = parts[0].strip()
                expr = parts[1].strip()
            else:
                label = None
                expr = line
            try:
                result = safe_eval(expr)
                if label:
                    print(f"{label} = {format_result(result)}")
                else:
                    print(f"{expr} = {format_result(result)}")
            except ValueError as e:
                print(f"ERROR: {e}")
        return

    use_json = sys.argv[1] == "--json"
    expressions = sys.argv[2:] if use_json else sys.argv[1:]

    if not expressions:
        print("Error: no expression provided")
        sys.exit(1)

    results = []
    for expr in expressions:
        try:
            result = safe_eval(expr)
            results.append({"expression": expr, "result": result, "error": None})
        except ValueError as e:
            results.append({"expression": expr, "result": None, "error": str(e)})

    if use_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            if r["error"]:
                print(f"ERROR [{r['expression']}]: {r['error']}")
            else:
                print(f"{r['expression']} = {format_result(r['result'])}")


if __name__ == "__main__":
    main()
