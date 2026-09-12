import os
import tempfile
import textwrap

import pytest

from doc_scout.extractor import extract_symbols

def write_temp_file(suffix, content):
    fd, path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(content))
    return path

def test_python_extractor():
    src = """
    def foo(a, b):
        return a + b

    class Bar:
        pass
    """
    path = write_temp_file(".py", src)
    symbols = extract_symbols(path)
    names = {s["name"] for s in symbols}
    assert "foo" in names
    assert "Bar" in names
    os.remove(path)

def test_js_extractor():
    src = """
    export function greet(name) {
        console.log(`Hello ${name}`);
    }

    export const add = (a, b) => a + b;

    export class Person {}
    """
    path = write_temp_file(".js", src)
    symbols = extract_symbols(path)
    names = {s["name"] for s in symbols}
    assert "greet" in names
    assert "add" in names
    assert "Person" in names
    os.remove(path)
"