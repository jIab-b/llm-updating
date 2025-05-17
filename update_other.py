
"""
Pull the current definition of a given function from update_target.py, show it to the OpenAI
API, receive a rewritten version, splice only that function back into
update_target.py, and reload the module so the running process immediately uses
the new code.
"""

from pathlib import Path
import ast
import importlib
import sys
import textwrap
from openai import OpenAI
import os

OPENAI_KEY="your key here"

TARGET_PATH = Path(__file__).with_name("update_target.py")


# ---------------------------------------------------------------------------#
# Helpers
# ---------------------------------------------------------------------------#
def get_function_source(path: Path, func_name: str):
    """
    Return (source_text, start_line, end_line, indent_spaces).
    """
    full_text = path.read_text(encoding="utf-8")
    tree = ast.parse(full_text)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            start = node.lineno - 1
            end = node.end_lineno
            lines = full_text.splitlines()[start:end]
            indent = len(lines[0]) - len(lines[0].lstrip())
            return "\n".join(lines), start, end, indent

    raise ValueError(f"Function {func_name!r} not found in {path}")


def ask_llm_for_rewrite(old_func_source: str, func_name: str) -> str:

    prompt = f"""
    Below is the current implementation of {func_name}() from update_target.py:

    ```python
    {old_func_source}

    Rewrite this function so that it prints a random string. generate the random string through the llm, 
    and dont import any new modules for the function"
    (and keep the same signature).

    Return ONLY the complete, updated function definition.
    """

    client = OpenAI(api_key=OPENAI_KEY)
    completion = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
    )
    return "\n".join(completion.choices[0].message.content.strip().splitlines()[1:-1])


def splice_function_into_file(
    path: Path,
    start: int,
    end: int,
    new_func_src: str,
    indent: int,
    ):
    lines = path.read_text(encoding="utf-8").splitlines()
    indented_new_src = textwrap.indent(new_func_src.strip("\n"), " " * indent).splitlines()
    lines[start:end] = indented_new_src
    path.write_text("\n".join(lines), encoding="utf-8")



def patch_func(target_func) -> None:

    old_src, start, end, indent = get_function_source(TARGET_PATH, target_func)
    new_src = ask_llm_for_rewrite(old_src, target_func)
    splice_function_into_file(TARGET_PATH, start, end, new_src, indent)


    module_name = os.path.splitext(os.path.basename(TARGET_PATH))[0]

    if module_name in sys.modules:
        importlib.reload(sys.modules[module_name])
    else:
        importlib.import_module(module_name)

def main():

    import update_target
    update_target.example_func()
    patch_func("example_func")
    update_target.example_func()


if __name__ == "__main__":
    main()

