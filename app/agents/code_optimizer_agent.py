import ast
import subprocess
import tempfile


def detect_inefficient_patterns(code):

    suggestions = []

    if "range(len(" in code:
        suggestions.append(
            "Avoid using range(len(list)). Use direct iteration instead."
        )

    if "== None" in code:
        suggestions.append(
            "Use 'is None' instead of '== None'."
        )

    return suggestions


def analyze_ast(code):

    suggestions = []

    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):

            if isinstance(node, ast.For):
                if isinstance(node.iter, ast.Call):
                    if getattr(node.iter.func, "id", "") == "range":
                        suggestions.append(
                            "Loop using range detected. Consider iterating directly."
                        )

    except Exception as e:
        suggestions.append(f"AST analysis error: {e}")

    return suggestions


def run_pyflakes(code):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        temp_file = f.name

    result = subprocess.run(
        ["pyflakes", temp_file],
        capture_output=True,
        text=True
    )

    return result.stdout


def format_code(code):

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        temp_file = f.name

    result = subprocess.run(
        ["autopep8", temp_file],
        capture_output=True,
        text=True
    )

    return result.stdout


def optimize_code(code):

    suggestions = []

    suggestions.extend(detect_inefficient_patterns(code))
    suggestions.extend(analyze_ast(code))

    errors = run_pyflakes(code)

    optimized = format_code(code)

    return suggestions, errors, optimized