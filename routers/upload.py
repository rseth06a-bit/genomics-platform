from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Sample, Sequence
from pipeline.parser import parse_fasta

router = APIRouter()

@router.post("/upload")
async def upload_fasta(file: UploadFile = File(...), db: Session = Depends(get_db)):
    #function that requires an uploaded file and database sesison that FastAPI gets with get_db
    if not file.filename.endswith((".fasta", ".fa", ".fna")):
        raise HTTPException(status_code=400, detail="File must be in FASTA format")

    contents = await file.read()
    #nonblocking request for file content
    
    sample = Sample(filename=file.filename)
    db.add(sample)
    db.commit()
    db.refresh(sample)
        #creates new Sample object, stages sample to be inserted, writes it to Postgres, and assigned id by Postgres

    sequences_added = 0
    #fasta_io = io.StringIO(contents.decode("utf-8"))
    records = parse_fasta(contents)
    #fast
    for record in records:
        seq = Sequence(
            sample_id=sample.id,
            header=record.description,
            raw_sequence=str(record.sequence),
            seq_length=len(record.sequence),
        )
        db.add(seq)
        sequences_added += 1
        #for everyrecord in the fasta file a new sequence is created and added to the db

    db.commit()

    return {
        "sample_id": sample.id,
        "filename": file.filename,
        "sequences_uploaded": sequences_added
    }
    #updates are commited and sample id, filename, and sequences added are returned