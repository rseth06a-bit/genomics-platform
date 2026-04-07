from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sample, Sequence
from Bio import SeqIO
import io

router = APIRouter()

@router.post("/upload")
async def upload_fasta(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".fasta", ".fa", ".fna")):
        raise HTTPException(status_code=400, detail="File must be in FASTA format")

    contents = await file.read()
    
    sample = Sample(filename=file.filename)
    db.add(sample)
    db.commit()
    db.refresh(sample)

    sequences_added = 0
    fasta_io = io.StringIO(contents.decode("utf-8"))
    for record in SeqIO.parse(fasta_io, "fasta"):
        seq = Sequence(
            sample_id=sample.id,
            header=record.id,
            raw_sequence=str(record.seq),
            seq_length=len(record.seq),
        )
        db.add(seq)
        sequences_added += 1

    db.commit()

    return {
        "sample_id": sample.id,
        "filename": file.filename,
        "sequences_uploaded": sequences_added
    }