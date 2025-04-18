# MCP Server Refactor & Feature Expansion: Detailed Planning Document

## 1. Refactor Server Code to Use JSON-RPC 2.0

**Objectives:**

- Ensure all server-client communications strictly follow JSON-RPC 2.0.
- Standardize request/response formats and error handling.

**Tasks:**

- [x] Audit current communication points (endpoints, handlers).
  - Located all REST endpoints and mapped them to new JSON-RPC methods.
- [x] Replace legacy/proprietary message formats with JSON-RPC 2.0.
  - All endpoints now use JSON-RPC 2.0 via fastapi-jsonrpc.
- [x] Implement JSON-RPC 2.0-compliant error responses.
  - Responses and errors now follow the JSON-RPC 2.0 spec.
- [x] Add capability negotiation (if not present).
  - Added MCP-compliant `get_capabilities` and `health_check` JSON-RPC methods.
- [ ] Update client(s) and documentation to reflect protocol changes.
- [x] Regression test all endpoints.
  - All tests pass and mypy reports no issues in server code.

**Progress Summary:**
- The server now fully supports JSON-RPC 2.0 for all communication.
- REST endpoints have been migrated.
- MCP-compliant health and capability methods are implemented.
- Type checking is clean (mypy passes with no errors).

---

## 2. Implement or Expand Resource Handlers

**Objectives:**

- Uniformly process and expose resources: Python, Markdown, PDF, web, and structured text.

**Tasks:**

- [ ] Define a base resource handler interface/abstract class.
- [ ] Implement/expand:
  - [ ] Python code handler (AST, docstrings, comments).
  - [ ] Markdown handler (sections, code blocks, links).
  - [ ] PDF handler (text extraction, sectionization).
  - [ ] Web handler (HTML parsing, main content extraction).
  - [ ] Structured text handler (YAML, JSON, TOML, XML).
- [ ] Add preprocessing/normalization for each type.
- [ ] Register handlers in server and expose via API.
- [ ] Write handler-specific tests.

---

## 3. Add or Update Callable Tools for Parsing & Feature Extraction

**Objectives:**

- Expose tools as callable endpoints/methods for LLM and client use.

**Tasks:**

- [ ] List required tools (e.g., AST parser, doc extractor, sectionizer).
- [ ] Standardize tool interface and registration.
- [ ] Implement or refactor each tool:
  - [ ] Python parsing.
  - [ ] Documentation extraction.
  - [ ] PDF/Markdown/Web feature extraction.
- [ ] Integrate tools into JSON-RPC 2.0 API.
- [ ] Document usage and add tests.

---

## 4. Build Out Prompt Management (Templating, Workflows, etc.)

**Objectives:**

- Manage prompts and workflows for LLM interaction and user input.

**Tasks:**

- [ ] Design prompt template format (Jinja2, string templates, etc.).
- [ ] Implement prompt storage, retrieval, and versioning.
- [ ] Build workflow engine (if required).
- [ ] Expose prompt management endpoints.
- [ ] Document prompt management system.

---

## 5. Integrate or Enhance Standardized Logging and Error Handling

**Objectives:**

- Ensure all logs and errors follow MCP and security best practices.

**Tasks:**

- [ ] Audit current logging and error handling.
- [ ] Refactor to use standardized logging utility.
- [ ] Add structured logs for key events (requests, errors, resource access).
- [ ] Ensure sensitive data is not logged.
- [ ] Implement error reporting in JSON-RPC 2.0 format.
- [ ] Add logging/error handling tests.

---

## 6. Write or Update Documentation and API Specs

**Objectives:**

- Provide clear, up-to-date documentation for all features and endpoints.

**Tasks:**

- [ ] Update or create OpenAPI/Swagger specs (if applicable).
- [ ] Write usage guides for all endpoints and tools.
- [ ] Document resource handler interfaces and prompt system.
- [ ] Add code comments and docstrings where missing.
- [ ] Prepare a migration guide for JSON-RPC 2.0 changes.

---

## 7. Plan and Add Tests for New Features

**Objectives:**

- Ensure robustness and compliance through automated testing.

**Tasks:**

- [ ] Identify test coverage gaps.
- [ ] Add unit tests for new/updated resource handlers.
- [ ] Add integration tests for JSON-RPC 2.0 endpoints.
- [ ] Add tests for tools, prompt management, and logging.
- [ ] Set up CI for automated test runs (if not present).

---

## Sequencing & Dependencies

1. Begin with JSON-RPC 2.0 refactor (prerequisite for API/tool changes).
2. Expand resource handlers and callable tools.
3. Build prompt management (depends on resource/tool APIs).
4. Integrate enhanced logging and error handling throughout.
5. Update documentation and specs as features are finalized.
6. Continuously add and update tests.
