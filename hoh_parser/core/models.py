from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class MCPFunction(BaseModel):
    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    parent: Optional[str] = None  # enclosing class or module
    docstring: Optional[str] = None

class MCPClass(BaseModel):
    name: str
    lineno: int
    col_offset: int
    end_lineno: Optional[int]
    bases: List[str] = []
    methods: List[MCPFunction] = []
    docstring: Optional[str] = None

class MCPRelationship(BaseModel):
    source: str
    target: str
    type: Literal[
        "defines", "calls", "inherits", "imports", "from-imports", "assigns",
        "overrides", "property", "property_setter", "property_deleter",
        "staticmethod", "classmethod", "composes"
    ]
    location: Optional[str] = None  # file or module

class MCPFile(BaseModel):
    path: str
    classes: List[MCPClass] = []
    functions: List[MCPFunction] = []
    relationships: List[MCPRelationship] = []
    docstring: Optional[str] = None
