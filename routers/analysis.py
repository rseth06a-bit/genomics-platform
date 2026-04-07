from fastapi import APIRouter
from pipeline.features import extract_features
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sample,Sequence

router = APIRouter()

@router.post("/analyze/{sample_id}")
def analyze(sample_id: int, db: Session=Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    sequences = db.query(Sequence).filter(Sequence.sample_id == sample_id).all()
    counter=0
    for sequence in sequences:
        features = extract_features(sequence.raw_sequence)
        sequence.gc_content = features["gc_content"]
        sequence.seq_length = features["seq_length"]
        sequence.kmer_json = features["kmer_json"]
        counter+=1
    db.commit()
    return(counter)

