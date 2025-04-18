import ast
from .models import MCPFile, MCPClass, MCPFunction, MCPRelationship
from typing import Any, List, Optional, Union

def extract_functions_and_classes(
    node: Union[ast.Module, ast.ClassDef, ast.FunctionDef],
    parent: Optional[str] = None
) -> tuple[List[MCPClass], List[MCPFunction]]:
    classes: List[MCPClass] = []
    functions: List[MCPFunction] = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.ClassDef):
            class_doc = ast.get_docstring(child)
            # Recursively extract methods and nested classes
            nested_classes, methods = extract_functions_and_classes(child, parent=child.name)
            bases = [base.id for base in child.bases if isinstance(base, ast.Name)]
            classes.append(MCPClass(
                name=child.name,
                lineno=child.lineno,
                col_offset=child.col_offset,
                end_lineno=getattr(child, "end_lineno", None),
                bases=bases,
                methods=methods,
                docstring=class_doc
            ))
            # Add nested classes to the result
            classes.extend(nested_classes)
        elif isinstance(child, ast.FunctionDef):
            # Recursively extract inner functions
            _, inner_functions = extract_functions_and_classes(child, parent=parent)
            functions.append(MCPFunction(
                name=child.name,
                lineno=child.lineno,
                col_offset=child.col_offset,
                end_lineno=getattr(child, "end_lineno", None),
                parent=parent,
                docstring=ast.get_docstring(child)
            ))
            functions.extend(inner_functions)
    return classes, functions

from typing import Dict, List

def extract_relationships(tree: ast.AST, filename: str) -> list[MCPRelationship]:
    relationships: list[MCPRelationship] = []
    class_methods = {}  # class name -> {method name: ast.FunctionDef}
    class_bases: Dict[str, List[str]] = {}    # class name -> [base class names]

    # First pass: collect class methods and bases
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = {}
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods[item.name] = item
            class_methods[node.name] = methods
            bases: list[str] = []
            for base in node.bases:
                if isinstance(base, ast.Name) and isinstance(base.id, str):
                    bases.append(base.id)
            class_bases[node.name] = bases

    # Second pass: relationships
    # Track parent class for assignment nodes to support correct 'composes' source
    node_to_parent_class: dict[int, str] = {}
    parent_class = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            parent_class = node.name
        if parent_class and isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            node_to_parent_class[id(node)] = parent_class
        # Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                relationships.append(MCPRelationship(
                    source=filename,
                    target=alias.name,
                    type="imports",
                    location=filename
                ))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                relationships.append(MCPRelationship(
                    source=filename,
                    target=f"{node.module}.{alias.name}" if node.module else alias.name,
                    type="from-imports",
                    location=filename
                ))
        # Variable assignments
        elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
            targets = []
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        targets.append(t.id)
                    elif isinstance(t, ast.Attribute):
                        assign_value: list[str] = []
                        assign_curr: ast.expr = t
                        while isinstance(assign_curr, ast.Attribute):
                            assign_value.insert(0, assign_curr.attr)
                            assign_curr = assign_curr.value
                        if isinstance(assign_curr, ast.Name):
                            assign_value.insert(0, assign_curr.id)
                        if assign_value:
                            targets.append(assign_value[-1])
            elif isinstance(node, ast.AnnAssign):
                t = node.target
                if isinstance(t, ast.Name):
                    targets.append(t.id)
                elif isinstance(t, ast.Attribute):
                    ann_value: list[str] = []
                    ann_curr: ast.expr = t
                    while isinstance(ann_curr, ast.Attribute):
                        ann_value.insert(0, ann_curr.attr)
                        ann_curr = ann_curr.value
                    if isinstance(ann_curr, ast.Name):
                        ann_value.insert(0, ann_curr.id)
                    if ann_value:
                        targets.append(ann_value[-1])
            elif isinstance(node, ast.AugAssign):
                t = node.target
                if isinstance(t, ast.Name):
                    targets.append(t.id)
                elif isinstance(t, ast.Attribute):
                    aug_value: list[str] = []
                    aug_curr: ast.expr = t
                    while isinstance(aug_curr, ast.Attribute):
                        aug_value.insert(0, aug_curr.attr)
                        aug_curr = aug_curr.value
                    if isinstance(aug_curr, ast.Name):
                        aug_value.insert(0, aug_curr.id)
                    if aug_value:
                        targets.append(aug_value[-1])
            # Composition: self.x = ClassName()
            for t in getattr(node, 'targets', []):
                if isinstance(t, ast.Attribute) and isinstance(t.value, ast.Name) and t.value.id == 'self':
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                        parent_class = node_to_parent_class.get(id(node), filename)
                        relationships.append(MCPRelationship(
                            source=parent_class,
                            target=node.value.func.id,
                            type="composes",
                            location=filename
                        ))
            for var in targets:
                relationships.append(MCPRelationship(
                    source=filename,
                    target=var,
                    type="assigns",
                    location=filename
                ))
        # Inheritance
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    relationships.append(MCPRelationship(
                        source=node.name,
                        target=base.id,
                        type="inherits",
                        location=filename
                    ))
            # Method overrides
            this_methods = class_methods.get(node.name, {})
            for base_name in class_bases.get(node.name, []):
                base_methods = class_methods.get(base_name, {})
                for m in this_methods:
                    if m in base_methods:
                        relationships.append(MCPRelationship(
                            source=f"{node.name}.{m}",
                            target=f"{base_name}.{m}",
                            type="overrides",
                            location=filename
                        ))
            # Property/static/classmethod detection (fixed: check all FunctionDefs in class body)
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    for deco in item.decorator_list:
                        if isinstance(deco, ast.Name):
                            if deco.id == 'property':
                                relationships.append(MCPRelationship(
                                    source=node.name,
                                    target=method_name,
                                    type="property",
                                    location=filename
                                ))
                            elif deco.id == 'staticmethod':
                                relationships.append(MCPRelationship(
                                    source=node.name,
                                    target=method_name,
                                    type="staticmethod",
                                    location=filename
                                ))
                            elif deco.id == 'classmethod':
                                relationships.append(MCPRelationship(
                                    source=node.name,
                                    target=method_name,
                                    type="classmethod",
                                    location=filename
                                ))
                        elif isinstance(deco, ast.Attribute):
                            # Handles @foo.setter and @foo.deleter
                            if deco.attr == 'setter':
                                relationships.append(MCPRelationship(
                                    source=node.name,
                                    target=method_name,
                                    type="property_setter",
                                    location=filename
                                ))
                            elif deco.attr == 'deleter':
                                relationships.append(MCPRelationship(
                                    source=node.name,
                                    target=method_name,
                                    type="property_deleter",
                                    location=filename
                                ))
                                source=node.name,
                                target=method_name,
        # Function calls
        elif isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            if func_name:
                relationships.append(MCPRelationship(
                    source=filename,
                    target=func_name,
                    type="calls",
                    location=filename
                ))
    return relationships

def parse_python_file(filepath: str) -> MCPFile:
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)
    docstring = ast.get_docstring(tree)
    classes, functions = extract_functions_and_classes(tree, parent=None)
    relationships = extract_relationships(tree, filename=filepath)
    return MCPFile(
        path=filepath,
        classes=classes,
        functions=functions,
        relationships=relationships,
        docstring=docstring
    )
