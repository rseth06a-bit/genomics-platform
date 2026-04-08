from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sample, Sequence
from pipeline.features import extract_features
from pipeline.ml import load_features, build_feature_matrix, train_sklearn_models, train_pytorch_model, predict
import json

router = APIRouter()  # ← this was missing

@router.post("/analyze/{sample_id}")
def analyze(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    sequences = db.query(Sequence).filter(Sequence.sample_id == sample_id).all()
    counter = 0
    for sequence in sequences:
        features = extract_features(sequence.raw_sequence)
        sequence.gc_content = features["gc_content"]
        sequence.seq_length = features["seq_length"]
        sequence.kmer_json  = features["kmer_json"]
        counter += 1
    db.commit()
    return counter

@router.get("/results/{sample_id}")
def get_results(sample_id: int, db: Session = Depends(get_db)):
    sample = db.query(Sample).filter(Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    sequences = db.query(Sequence).filter(Sequence.sample_id == sample_id).all()
    if not sequences:
        raise HTTPException(status_code=404, detail="No sequences found — run /analyze first")
    results = []
    for seq in sequences:
        prediction = None
        if seq.kmer_json and seq.gc_content is not None:
            try:
                prediction = predict({
                    "gc_content": seq.gc_content,
                    "seq_length": seq.seq_length,
                    "kmer_json": seq.kmer_json
                })
            except Exception as e:
                prediction = {"error": str(e)}
        results.append({
            "sequence_id": seq.id,
            "gc_content": seq.gc_content,
            "seq_length": seq.seq_length,
            "kmers": json.loads(seq.kmer_json) if seq.kmer_json else None,
            "predictions": prediction
        })
    return {"sample_id": sample_id, "sequences": results}

@router.post("/train")
def train(db: Session = Depends(get_db)):
    seq_list, labels = load_features(db)
    if len(seq_list) < 5:
        raise HTTPException(status_code=400, detail="Not enough sequences to train (need at least 5)")
    X = build_feature_matrix(seq_list)
    train_sklearn_models(X, labels)
    train_pytorch_model(X, labels)
    return {"status": "training complete", "samples_used": len(seq_list)}