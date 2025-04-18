"""
Test file for class inheritance extraction.
"""

def test_inheritance_extraction(tmp_path):
    code = '''
class Base:
    pass

class Child(Base):
    def foo(self):
        pass
'''
    test_file = tmp_path / "inheritance_sample.py"
    test_file.write_text(code)

    from HoH_parser.core.parser import parse_python_file
    mcp_file = parse_python_file(str(test_file))
    # Look for the inheritance relationship
    inherits = [rel for rel in mcp_file.relationships if rel.type == "inherits"]
    assert any(rel.source == "Child" and rel.target == "Base" for rel in inherits), "Inheritance relationship not found!"
    # Also check the class is present
    assert any(cls.name == "Child" for cls in mcp_file.classes), "Child class not found!"
    assert any(cls.name == "Base" for cls in mcp_file.classes), "Base class not found!"
