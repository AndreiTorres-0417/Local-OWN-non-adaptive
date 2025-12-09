from fastapi import APIRouter

from .placement import router as placement_router
from .assessment import router as assessment_router
from .results import router as results_router
from .diagnostic import router as diagnostic_router   # Non adaptive

router = APIRouter()

router.include_router(placement_router)
router.include_router(assessment_router)
router.include_router(results_router)
router.include_router(diagnostic_router)  # Non adaptive

