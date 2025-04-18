from fastapi import APIRouter, UploadFile, File, Query
from hoh_mcp.core.parser import parse_python_file
from hoh_mcp.core.models import MCPFile
import tempfile

router = APIRouter()

@router.post("/parse-file", response_model=MCPFile)
async def parse_file_endpoint(file: UploadFile = File(...)) -> MCPFile:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    result = parse_python_file(tmp_path)
    return result

@router.get("/symbol-table")
async def symbol_table_query(filepath: str = Query(...)) -> dict:
    result = parse_python_file(filepath)
    return result.model_dump()
