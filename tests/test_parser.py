import tempfile
from HoH_parser.core.parser import parse_python_file
import os
import json
from HoH_parser.core.models import MCPFile

def test_parse_simple_function() -> None:
    code = (
        "def foo(x: int) -> int:\n"
        "    \"\"\"Returns x squared.\"\"\"\n"
        "    return x * x\n"
    )
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py", delete=False) as tmp:
        tmp.write(code)
        tmp.flush()
        result = parse_python_file(tmp.name)
        print("\nFull MCPFile symbol output:")
        print(result.model_dump_json(indent=2))
        assert result.functions[0].name == "foo"
        assert result.functions[0].docstring == "Returns x squared."
        assert result.functions[0].parent is None

def test_parse_real_code_file() -> None:
    """Test parsing a real code file (parser.py itself)"""
    parser_path = os.path.join(os.path.dirname(__file__), "../HoH_parser/core/parser.py")
    parser_path = os.path.abspath(parser_path)
    result = parse_python_file(parser_path)
    print("\nFull MCPFile symbol output for parser.py:")
    print(result.model_dump_json(indent=2))
    assert any(f.name == "parse_python_file" for f in result.functions)

def test_parse_large_input_file(tmp_path) -> None:
    """Test parsing a synthetic large input file, not dependent on external modules."""
    code = '''
class Outer:
    class Inner:
        def inner_method(self):
            pass
    def outer_method(self):
        def nested_func():
            x = 1
            x += 2
            return x
        return nested_func()

def top_level_func():
    y = 5
    return y

class Parent:
    pass

class Child(Parent):
    def child_method(self):
        return "child"
'''
    test_file = tmp_path / "synthetic_large.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    print("Full MCPFile symbol output for synthetic_large.py:")
    print(json.dumps(result.model_dump(), indent=2))
    # Check for nested classes, inheritance, and function relationships
    assert any(cls.name == "Outer" for cls in result.classes)
    assert any(cls.name == "Inner" for cls in result.classes)
    assert any(cls.name == "Parent" for cls in result.classes)
    assert any(cls.name == "Child" for cls in result.classes)
    inherits = [rel for rel in result.relationships if rel.type == "inherits"]
    assert any(rel.source == "Child" and rel.target == "Parent" for rel in inherits)
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    assert any(rel.target == "x" for rel in assigns)
    assert any(rel.target == "y" for rel in assigns)
    calls = [rel for rel in result.relationships if rel.type == "calls"]
    assert any(rel.target == "nested_func" for rel in calls)
    assert isinstance(result, MCPFile)

def test_complex_inheritance(tmp_path) -> None:
    """Test multiple inheritance and indirect inheritance."""
    code = '''
class A: pass
class B: pass
class C(A, B): pass
class D(C): pass
'''
    test_file = tmp_path / "complex_inheritance.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    inherits = [rel for rel in result.relationships if rel.type == "inherits"]
    # C inherits from A and B, D inherits from C
    assert any(rel.source == "C" and rel.target == "A" for rel in inherits)
    assert any(rel.source == "C" and rel.target == "B" for rel in inherits)
    assert any(rel.source == "D" and rel.target == "C" for rel in inherits)

def test_decorated_methods(tmp_path) -> None:
    """Test decorated methods and functions."""
    code = '''
def deco(func):
    def wrapper(*a, **k): return func(*a, **k)
    return wrapper

class X:
    @deco
    def foo(self): return 1

@deco
def bar(): return 2
'''
    test_file = tmp_path / "decorated_methods.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    # Should still find foo and bar as functions
    assert any(f.name == "foo" for f in result.functions) or any("foo" in m.name for c in result.classes for m in c.methods)
    assert any(f.name == "bar" for f in result.functions)

def test_edge_cases_empty_and_pass(tmp_path) -> None:
    """Test empty classes and pass-only bodies."""
    code = '''
class Empty: pass
class OnlyPass:
    def foo(self): pass
'''
    test_file = tmp_path / "edge_cases.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assert any(cls.name == "Empty" for cls in result.classes)
    assert any(cls.name == "OnlyPass" for cls in result.classes)
    # Should find method foo
    assert any(m.name == "foo" for c in result.classes for m in c.methods)

def test_attribute_access_and_override(tmp_path) -> None:
    """Test attribute access and method override detection (if supported)."""
    code = '''
class Base:
    def method(self):
        self.x = 1
        return self.x
class Sub(Base):
    def method(self):
        self.x = 2
        return self.x
'''
    test_file = tmp_path / "attr_override.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    # Should see assignment to x
    assert any(rel.target == "x" for rel in assigns)
    # If method override detection is implemented, check for it (future expansion)
    # For now, just ensure both methods are found
    assert sum(m.name == "method" for c in result.classes for m in c.methods) == 2

def test_annassign_attribute(tmp_path) -> None:
    code = '''
class Foo:
    def bar(self):
        self.x: int = 42
    '''
    test_file = tmp_path / "annassign_attr.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    assert any(rel.target == "x" for rel in assigns)

def test_augassign_attribute(tmp_path) -> None:
    code = '''
class Foo:
    def bar(self):
        self.x = 1
        self.x += 2
    '''
    test_file = tmp_path / "augassign_attr.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    assert any(rel.target == "x" for rel in assigns)

def test_annassign_local(tmp_path) -> None:
    code = '''
def foo():
    x: int = 42
    '''
    test_file = tmp_path / "annassign_local.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    assert any(rel.target == "x" for rel in assigns)

def test_augassign_local(tmp_path) -> None:
    code = '''
def foo():
    x = 1
    x += 2
    '''
    test_file = tmp_path / "augassign_local.py"
    test_file.write_text(code)
    result = parse_python_file(str(test_file))
    assigns = [rel for rel in result.relationships if rel.type == "assigns"]
    assert any(rel.target == "x" for rel in assigns)

def test_parser_relationships_enhancements():
    code = '''
class Bar:
    pass

class Foo:
    def __init__(self):
        self.bar = Bar()

    @property
    def x(self): return 1

    @x.setter
    def x(self, value): pass

    @x.deleter
    def x(self): pass

    @staticmethod
    def sm(): pass

    @classmethod
    def cm(cls): pass
'''
    import ast
    from HoH_parser.core.parser import extract_relationships

    tree = ast.parse(code)
    rels = extract_relationships(tree, "testfile.py")
    rel_types = {(r.source, r.target, r.type) for r in rels}


    assert ("Foo", "Bar", "composes") in rel_types
    assert ("Foo", "x", "property") in rel_types
    assert ("Foo", "x", "property_setter") in rel_types
    assert ("Foo", "x", "property_deleter") in rel_types
    assert ("Foo", "sm", "staticmethod") in rel_types
    assert ("Foo", "cm", "classmethod") in rel_types
