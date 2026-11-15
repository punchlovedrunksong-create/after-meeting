from fastapi import APIRouter, File, UploadFile

from app.agents.workflow import AnalysisWorkflow
from app.api.schemas.analysis import AnalysisResponse
from app.models.analysis import AnalysisResult
from app.services.document_service import DocumentService

router = APIRouter(prefix="/v1/analyses", tags=["analyses"])
document_service = DocumentService()
analysis_workflow = AnalysisWorkflow()


@router.post("", response_model=AnalysisResponse, response_model_exclude_none=True)
async def create_analysis(file: UploadFile = File(...)) -> AnalysisResult:
    """Validate an uploaded TXT file and return its summary and todo items."""
    try:
        meeting_text = await document_service.read_txt(file)
        return await analysis_workflow.run(meeting_text)
    finally:
        await file.close()
