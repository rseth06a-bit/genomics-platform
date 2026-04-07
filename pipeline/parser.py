from dataclasses import dataclass
from Bio import SeqIO
import io

@dataclass
class FASTARecord:
    seq_id: str
    sequence: str
    description: str

def parse_fasta(raw_data: bytes):
    seq_list = []
    fasta_io = io.StringIO(raw_data.decode("utf-8"))
    for record in SeqIO.parse(fasta_io, "fasta"):
        seq_list.append(FASTARecord(record.id, str(record.seq), record.description))
    return seq_list

