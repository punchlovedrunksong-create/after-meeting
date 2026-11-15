from pydantic import BaseModel, ConfigDict

from app.models.analysis import AnalysisResult


class AnalysisErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    action: str


class AnalysisResponse(AnalysisResult):
    """HTTP response shape for a completed analysis."""
