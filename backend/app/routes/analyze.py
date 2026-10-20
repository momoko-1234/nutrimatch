"""Analysis API route."""

from fastapi import APIRouter

from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.personalized_advice import build_personalized_advice
from app.services.ollama_analysis import add_local_analysis


router = APIRouter(prefix="/api", tags=["analysis"])


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Analyze user profile and return personalized nutrition advice."""

    return add_local_analysis(payload, build_personalized_advice(payload))
