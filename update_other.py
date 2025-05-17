


# hot_patch_utils.py
from pathlib import Path
import importlib, sys, ast, textwrap, openai

UPDATE_FILE_PATH = Path(__file__).with_name("utils.py")
UPDATE_FUNC  = "foo"


# ---------- helpers ----------------------------------------------------------

def _current_function_source(path: Path, func_name: str) -> tuple[str, int, int]:
    """
    Return (source_text, start_line, end_line) for func_name inside *path*.
    Lines are 0-based and inclusive of start, exclusive of end.
    """
    src  = path.read_text(encoding="utf-8")
    tree = ast.parse(src)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            start, end = node.lineno - 1, node.end_lineno        # 0-based slice
            lines = src.splitlines()[start:end]
            return "\n".join(lines), start, end

    raise ValueError(f"Function {func_name} not found in {path}")


def _ask_llm_for_new_source(old_func_src: str) -> str:
    """
    Give the current version of foo() to the LLM and ask it to return ONLY
    the rewritten function definition.
    """
    prompt = f"""
You are an expert Python programmer.

Below is the current implementation of {FUNC_NAME}() from utils.py:

```python
{old_func_src}