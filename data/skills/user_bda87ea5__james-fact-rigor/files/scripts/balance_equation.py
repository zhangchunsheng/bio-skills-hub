#!/usr/bin/env python3
"""
Chemical equation balance checker for fact-rigor skill.
Parses a chemical equation and verifies atom balance on both sides.

Usage:
    python3 scripts/balance_equation.py "2H2 + O2 -> 2H2O"
    python3 scripts/balance_equation.py "CH4 + 2O2 -> CO2 + 2H2O"
    python3 scripts/balance_equation.py --strict "N2 + 3H2 -> 2NH3"

The script:
1. Parses each compound and its coefficient
2. Counts atoms of each element on each side
3. Reports whether the equation is balanced
4. If unbalanced, shows the discrepancy per element

Use -> or = to separate reactants from products.
Use + to separate compounds.
"""

import sys
import re
from collections import defaultdict


def parse_compound(formula: str):
    """
    Parse a chemical formula into element counts.
    Handles: H2O, CO2, Ca(OH)2, 2H2O, H2SO4, Al2(SO4)3
    Returns: dict of {element: count}
    """
    formula = formula.strip()

    # Extract leading coefficient (e.g., "2" from "2H2O")
    coeff_match = re.match(r"^(\d+)(.*)", formula)
    if coeff_match:
        coeff = int(coeff_match.group(1))
        formula = coeff_match.group(2)
    else:
        coeff = 1

    elements = defaultdict(int)

    # Handle parenthesized groups: (OH)2, (SO4)3
    def parse_group(text, multiplier=1):
        i = 0
        while i < len(text):
            if text[i] == '(':
                # Find matching closing paren
                depth = 1
                j = i + 1
                while j < len(text) and depth > 0:
                    if text[j] == '(':
                        depth += 1
                    elif text[j] == ')':
                        depth -= 1
                    j += 1
                inner = text[i+1:j-1]
                # Check for group multiplier after closing paren
                after = text[j:]
                mult_match = re.match(r"^(\d*)", after)
                group_mult = int(mult_match.group(1)) if mult_match.group(1) else 1
                parse_group(inner, multiplier * group_mult)
                i = j + (len(mult_match.group(1)) if mult_match else 0)
            elif text[i].isupper():
                # Element symbol: uppercase followed by optional lowercase
                elem_match = re.match(r"^([A-Z][a-z]?)(\d*)", text[i:])
                if elem_match:
                    elem = elem_match.group(1)
                    count = int(elem_match.group(2)) if elem_match.group(2) else 1
                    elements[elem] += count * multiplier
                    i += len(elem_match.group(0))
                else:
                    i += 1
            elif text[i].isdigit():
                # Standalone number (shouldn't happen after extraction)
                i += 1
            else:
                i += 1

    parse_group(formula)

    # Apply leading coefficient
    for elem in elements:
        elements[elem] *= coeff

    return dict(elements), coeff


def parse_equation(equation: str):
    """
    Parse a full equation into reactant and product atom counts.
    Returns: (reactants_total, products_total, parsed_compounds)
    """
    equation = equation.strip()

    # Split on -> or =
    if "->" in equation:
        left, right = equation.split("->", 1)
    elif "=" in equation:
        left, right = equation.split("=", 1)
    else:
        return None, None, None, "Equation must contain '->' or '='"

    def parse_side(side: str):
        compounds = [c.strip() for c in side.split("+") if c.strip()]
        total = defaultdict(int)
        parsed = []
        for comp in compounds:
            elements, coeff = parse_compound(comp)
            parsed.append({"compound": comp, "coefficient": coeff, "elements": elements})
            for elem, count in elements.items():
                total[elem] += count
        return dict(total), parsed

    reactants, reactant_compounds = parse_side(left)
    products, product_compounds = parse_side(right)

    return reactants, products, {"reactants": reactant_compounds, "products": product_compounds}, None


def check_balance(equation: str, strict: bool = False):
    """Check if equation is balanced. Returns result dict."""
    reactants, products, parsed, error = parse_equation(equation)

    if error:
        return {"balanced": False, "error": error, "equation": equation}

    all_elements = sorted(set(list(reactants.keys()) + list(products.keys())))

    discrepancies = []
    for elem in all_elements:
        left_count = reactants.get(elem, 0)
        right_count = products.get(elem, 0)
        if left_count != right_count:
            discrepancies.append({
                "element": elem,
                "reactants": left_count,
                "products": right_count,
                "difference": right_count - left_count
            })

    balanced = len(discrepancies) == 0

    result = {
        "equation": equation,
        "balanced": balanced,
        "reactants": reactants,
        "products": products,
        "discrepancies": discrepancies,
        "parsed": parsed,
    }

    if strict and not balanced:
        result["error"] = "Equation is NOT balanced"

    return result


def print_result(result):
    """Print human-readable result."""
    if result.get("error") and "parsed" not in result:
        print(f"❌ Error: {result['error']}")
        return

    print(f"Equation: {result['equation']}")
    print()

    if result["parsed"]:
        print("Reactants:")
        for comp in result["parsed"]["reactants"]:
            elems = ", ".join(f"{k}: {v}" for k, v in comp["elements"].items())
            print(f"  {comp['coefficient']}× {comp['compound'].lstrip('0123456789')} → {elems}")
        print("Products:")
        for comp in result["parsed"]["products"]:
            elems = ", ".join(f"{k}: {v}" for k, v in comp["elements"].items())
            print(f"  {comp['coefficient']}× {comp['compound'].lstrip('0123456789')} → {elems}")
        print()

    print("Atom count comparison:")
    all_elements = sorted(set(
        list(result["reactants"].keys()) + list(result["products"].keys())
    ))
    print(f"  {'Element':<8} {'Reactants':>10} {'Products':>10} {'Status':>10}")
    print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10}")
    for elem in all_elements:
        left = result["reactants"].get(elem, 0)
        right = result["products"].get(elem, 0)
        status = "✅" if left == right else "❌"
        print(f"  {elem:<8} {left:>10} {right:>10} {status:>10}")

    print()
    if result["balanced"]:
        print("✅ Equation is balanced.")
    else:
        print("❌ Equation is NOT balanced.")
        if result["discrepancies"]:
            print("Discrepancies:")
            for d in result["discrepancies"]:
                diff = d["difference"]
                direction = "more on products side" if diff > 0 else "more on reactants side"
                print(f"  {d['element']}: reactants={d['reactants']}, products={d['products']} ({abs(diff)} {direction})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 balance_equation.py \"EQUATION\" [--strict]")
        print()
        print("Examples:")
        print('  python3 balance_equation.py "2H2 + O2 -> 2H2O"')
        print('  python3 balance_equation.py "CH4 + 2O2 -> CO2 + 2H2O"')
        print('  python3 balance_equation.py "N2 + 3H2 -> 2NH3"')
        print('  python3 balance_equation.py "2H2 + O2 -> H2O"  # intentionally unbalanced')
        sys.exit(0)

    strict = "--strict" in sys.argv
    equations = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not equations:
        print("Error: no equation provided")
        sys.exit(1)

    for eq in equations:
        print_result(check_balance(eq, strict=strict))
        print()
        print("=" * 50)
        print()


if __name__ == "__main__":
    main()
