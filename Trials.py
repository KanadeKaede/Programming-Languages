"""
Laboratory Activity No. 2 - From Syntax to Semantics
Recursive-descent recognizer (Task A) and evaluator (Task B) for the grammar:

    <expr>   -> <term> { (+ | -) <term> }
    <term>   -> <factor> { (* | /) <factor> }
    <factor> -> ( <expr> ) | <digit>
    <digit>  -> 0|1|2|3|4|5|6|7|8|9

Design: the input string is spliced into a list of individual characters.
Since lists are mutable, every parse_* function can pop characters off the
FRONT of that same shared list -- so there's no position counter or class
to maintain, every function just sees whatever is left after the deeper
calls consumed their part. Task A and Task B happen in one pass: each
parse_* function checks the grammar rule AND computes the value using
Python's own +, -, *, / as it goes. If the grammar doesn't match, a
ValueError is raised and no value is ever produced.
"""


def parse_expr(chars, original):
    # <expr> -> <term> { (+ | -) <term> }
    value = parse_term(chars, original)
    while chars and chars[0] in ("+", "-"):
        op = chars.pop(0)
        rhs = parse_term(chars, original)
        value = value + rhs if op == "+" else value - rhs
    return value


def parse_term(chars, original):
    # <term> -> <factor> { (* | /) <factor> }
    value = parse_factor(chars, original)
    while chars and chars[0] in ("*", "/"):
        op = chars.pop(0)
        rhs = parse_factor(chars, original)
        if op == "*":
            value = value * rhs
        else:
            if rhs == 0:
                raise ValueError(f"division by zero (position {len(original) - len(chars)})")
            value = value / rhs
    return value


def parse_factor(chars, original):
    # <factor> -> ( <expr> ) | <digit>   < recursion happens here,
    # when '(' sends us back up to parse_expr()
    if not chars:
        raise ValueError(f"unexpected end of input (position {len(original)})")

    c = chars[0]
    if c == "(":
        chars.pop(0)
        value = parse_expr(chars, original)
        if not chars or chars[0] != ")":
            pos = len(original) - len(chars)
            raise ValueError(f"expected ')' (position {pos})")
        chars.pop(0)
        return value
    elif c in "0123456789":
        chars.pop(0)
        return int(c)
    else:
        pos = len(original) - len(chars)
        raise ValueError(f"unexpected token '{c}' (position {pos})")


def check_and_evaluate(expression):
    """Task A (syntax check) + Task B (semantic evaluation) combined."""
    chars = list(expression)  # splice the input into individual characters
    try:
        value = parse_expr(chars, expression)
        if chars:  # leftover characters after a full expression = invalid
            pos = len(expression) - len(chars)
            raise ValueError(f"unexpected token '{chars[0]}' (position {pos})")
    except ValueError as e:
        print(f"  Invalid syntax: {e}")
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)
    print(f"  Valid syntax -> Value: {value}")
    return value


def naive_left_to_right_eval(expression):
    """
    Stretch requirement: evaluator for the AMBIGUOUS grammar
        <expr> -> <expr> + <expr> | <expr> * <expr> | <digit>
    with no precedence -- folds left to right, digit by digit.
    Assumes single-digit operands and no parentheses, same as the test case.
    """
    chars = list(expression)
    value = int(chars.pop(0))
    while chars:
        op = chars.pop(0)
        rhs = int(chars.pop(0))
        value = value + rhs if op == "+" else value * rhs
    return value


def demonstrate_ambiguity():
    expr = "2+3*4"
    naive_result = naive_left_to_right_eval(expr)
    correct_result = parse_expr(list(expr), expr)
    print(f"Ambiguity demo on '{expr}':")
    print(f"  Naive left-to-right (ambiguous grammar): {naive_result}")
    print(f"  Correct precedence (Section II grammar): {correct_result}")
    print(
        "  -> The ambiguous grammar lets '2+3*4' be parsed two different ways, "
        "so it has no single meaning. Section II's grammar fixes this by "
        "putting <term> (*, /) below <expr> (+, -) in the hierarchy, forcing "
        "* and / to bind tighter, and by using left-recursive repetition so "
        "same-precedence operators are evaluated left to right."
    )


def main():
    print("=== Stretch Requirement: Ambiguity Demonstration ===")
    demonstrate_ambiguity()

    print("\n=== Required Test Cases ===")
    test_cases = ["3+4*2", "(3+4)*2", "8/2-1", "3++4", "(3+4", "2+3*4"]
    for tc in test_cases:
        print(f"Input: {tc}")
        check_and_evaluate(tc)

    print("\n=== Try your own input ===")
    user_input = input("Enter an expression: ").strip()
    print(f"Input: {user_input}")
    check_and_evaluate(user_input)


if __name__ == "__main__":
    main()
