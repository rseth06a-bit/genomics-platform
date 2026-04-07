from fastapi import APIRouter

router = APIRouter()

@router.post("/analyze/{sample_id}")
def analyze(sample_id: int):
    return {"message": f"Analysis for sample {sample_id} not yet implemented"}