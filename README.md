
# HoH-mcp: Local Python Code Parsing MCP Server

# (Hammer of Hephaestus Model Context Protocol Server)

## Overview

HoH-mcp is a privacy-first, locally-run MCP (Model Context Protocol) server designed to parse Python codebases, extract rich code structure, and prepare data for ingestion into knowledge graphs like ArangoDB. Unlike cloud-based or proprietary solutions (like codegen or codegen-mcp-server), HoH-mcp uses only open-source, local tools—ensuring your code never leaves your environment.

## Motivation

No Cloud Dependency: All parsing and analysis are performed locally—no code or PII is ever sent to external services.
Full Control: You own and can extend every part of the parsing, modeling, and ingestion process.
Extensibility: Designed to support additional languages, richer analyses, and new output formats as your needs grow.

## Levels of Code Abstraction

File Level: Too coarse for semantic search or graph construction.
Class/Function Level: The ideal primary node level—functions and classes encapsulate meaningful, reusable logic and relationships.
Statement/Clause Level: Too granular; loses context and makes the graph noisy.
Block/Logical Chunk Level: Useful for chunking large functions for embeddings, but not as primary graph nodes.

## Recommendation:

Use functions and classes as your main code objects (nodes in the graph). Attach metadata (line ranges, docstrings, called functions, etc.) as needed.
Relationships to model:

- CALLS (function calls function)
- CONTAINS (class contains function, file contains class/function)
- INHERITS/IMPLEMENTS (class relationships)
- REFERENCES (variable, attribute, import usage)

## Example: ArangoDB Document Structure

### Function Node Example:

```json
{
  "_key": "my_module.my_function",
  "type": "function",
  "name": "my_function",
  "qualified_name": "my_module.my_function",
  "source_code": "def my_function(x): ...",
  "docstring": "This function does X.",
  "embedding": [0.123, 0.456, ...],
  "start_line": 10,
  "end_line": 25,
  "parent": "my_module",
  "calls": ["other_module.other_function"],
  // ...other metadata
}
```

### Class Node Example:

```json
{
  "_key": "my_module.MyClass",
  "type": "class",
  "name": "MyClass",
  "qualified_name": "my_module.MyClass",
  "source_code": "class MyClass:\n    ...",
  "docstring": "Class for doing Y.",
  "embedding": [0.111, 0.222, 0.333, ...],
  "start_line": 1,
  "end_line": 50,
  "parent": "my_module",
  "methods": ["my_module.MyClass.method_a", "my_module.MyClass.method_b"],
  "inherits_from": ["BaseClass"],
  "contained_in": "my_module",
  "file_path": "src/my_module.py",
  "created_at": "2025-04-17T09:43:00Z",
  "last_modified": "2025-04-17T09:43:00Z"
}
```

### Edge Example (CALLS, CONTAINS, INHERITS):

```json
{
  "_from": "functions/my_module.my_function",
  "_to": "functions/other_module.other_function",
  "type": "CALLS",
  "weight": 0.9
}
```

## Core Architectural Principles

Modularity: Separate parsing, data modeling, API serving, and ingestion logic.
Extensibility: Add new languages, analyses, or output formats easily.
Reusability: Core parsing logic is usable as both a CLI and a long-running service.
Maintainability: Clear boundaries, tests, and documentation.

## Recommended Component Breakdown

### Parsing Engine

Walks the codebase, parses files, and extracts symbols using Python’s ast or LibCST.
Outputs a structured, in-memory representation (symbol table as dicts or dataclasses).

### MCP Data Models

Internal schema for code objects (functions, classes, files, relationships).
Use Python dataclasses or Pydantic models for type safety and validation.

### API Layer (Service)

**All API communication is now via JSON-RPC 2.0 at `/jsonrpc/`.**

- Parsing files/directories
- Querying symbol tables
- Getting code object details
- Health and capability checks (MCP-compliant)

Built with FastAPI and [fastapi-jsonrpc](https://github.com/liyasthomas/fastapi-jsonrpc).

#### Example: JSON-RPC Request (with curl)

Parse a file (base64-encoded content):

```bash
curl -X POST http://localhost:8000/jsonrpc/ \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "method": "parse_file",
    "params": {"filename": "foo.py", "content_b64": "<base64-encoded-content>"},
    "id": 1
  }'
```

Get capabilities:

```bash
curl -X POST http://localhost:8000/jsonrpc/ \
  -H 'Content-Type: application/json' \
  -d '{
    "jsonrpc": "2.0",
    "method": "get_capabilities",
    "params": {},
    "id": 2
  }'
```

See `MCP_Integration.md` for more details about the protocol and available methods.

**Note:** The previous REST API has been fully replaced by JSON-RPC 2.0 endpoints.
### Ingestion/Export Layer

Takes MCP objects and inserts them into ArangoDB, or exports as JSON, etc.
Decoupled from parsing logic.

### CLI Interface (Optional)

For batch operations, debugging, or scripting.

## Example Directory Structure

```bash
hoh_parser_Server/
├── __init__.py
├── main.py           # API entrypoint (FastAPI app)
├── parser.py         # Core parsing logic (AST/LibCST)
├── models.py         # MCP dataclasses/Pydantic models
├── ingestion.py      # ArangoDB (or other) ingestion logic
├── utils.py          # Helpers, config, etc.
├── cli.py            # Optional CLI interface
└── tests/            # Unit/integration tests
```

## Example: MCP Data Model (Dataclass)

```python
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class FunctionSymbol:
    name: str
    qualified_name: str
    docstring: Optional[str]
    signature: str
    start_line: int
    end_line: int
    parent: Optional[str]
    calls: List[str] = field(default_factory=list)
    source_code: Optional[str] = None

@dataclass
class ClassSymbol:
    name: str
    qualified_name: str
    docstring: Optional[str]
    methods: List[FunctionSymbol]
    inherits_from: List[str]
    start_line: int
    end_line: int
    parent: Optional[str]
    source_code: Optional[str] = None
```

## Example: FastAPI Endpoint Skeleton

```python
from fastapi import FastAPI, Query
from parser import parse_file  # your core parser logic

app = FastAPI()

@app.get("/parse")
def parse_endpoint(path: str):
    symbols = parse_file(path)
    return {"symbols": [s.to_dict() for s in symbols]}
```

## Why This Structure?

- Separation of concerns: Each part is testable and replaceable.
- Extensible: Add new endpoints, language support, or output formats.
- Integrates with IDEs, CI/CD, and other tools: Just call the API or CLI.

## Development & Testing Status

- All endpoints are now JSON-RPC 2.0-compliant as of 2025-04-18.
- MCP-compliant `health_check` and `get_capabilities` methods are implemented.
- All automated tests and mypy pass as of 2025-04-18.

## Next Steps

- Scaffold a new repository for HoH-mcp.
  - Develop the parsing engine and MCP data models.
  - Add API endpoints for parsing and symbol table queries.
  - Implement ingestion/export logic for ArangoDB.
  - Integrate with your knowledge graph pipeline.

## Summary

HoH-mcp will be a robust, local, and extensible MCP server for Python code parsing, symbol extraction, and knowledge graph ingestion—built entirely with open-source tools, and never sending any code to the cloud.
