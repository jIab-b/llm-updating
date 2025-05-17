
def self_update():
    import openai, inspect, textwrap, types, os, sys

    # 1) Ask the LLM for a new body of the function
    prompt = "Rewrite the function so it prints 'Hello, new world!'"
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    new_body = response.choices[0].message.content

    # 2) Build complete source text for the function object
    func_name = self_update.__name__
    header = f"def {func_name}():\n"
    indented = textwrap.indent(new_body, "    ")
    new_src = header + indented + "\n"

    # 3) Compile it and graft it onto the old function object
    code = compile(new_src, filename="<ai>", mode="exec")
    ns: dict[str, object] = {}
    exec(code, self_update.__globals__, ns)
    self_update.__code__ = ns[func_name].__code__   # hot-swap

# First call uses original version
self_update()
# Second call uses LLM-generated version
self_update()