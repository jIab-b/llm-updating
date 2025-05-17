from pathlib import Path
import ast
import importlib
import sys
import textwrap
from openai import OpenAI
import os

OPENAI_KEY="your key here"

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



def self_update():
    from openai import OpenAI
    import openai, inspect, textwrap, types, os, sys

    print_msg = "l;akdsfjkl;"
    print(print_msg)

    self_name = Path(__file__).with_name("update_self.py")
    self_src = get_function_source(self_name, "self_update")
    prompt = f"""
    Below is the current implementation of this function from update_self.py:

    ```python
    {self_src}

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
    new_body = "\n".join(completion.choices[0].message.content.strip().splitlines()[1:-1])
    with open('save.txt', "w", encoding="utf-8") as f:
        f.write(new_body)


    func_name = self_update.__name__

    # Compile it and graft it onto the old function object
    code = compile(new_body, filename="<ai>", mode="exec")
    ns: dict[str, object] = {}
    exec(code, self_update.__globals__, ns)
    self_update.__code__ = ns[func_name].__code__   # hot-swap


self_update()
self_update()