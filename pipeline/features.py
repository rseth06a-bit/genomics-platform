from collections import Counter
import json

#returns proportion of Gs and Cs and num between 1 and 0
def gc_content(sequence):
    num_g=0
    num_c=0
    sequence = sequence.upper()
    for c in sequence:
        if c=="G": 
            #case sensitive and also sequence always upper case
            num_g+=1
        elif c=="C":
            num_c+=1
    if (len(sequence)==0):
        gc_content_num=0
    else:
        gc_content_num=((num_g+num_c)/(len(sequence)))
    return (gc_content_num)

#returns all k-mers in sequence as array     
def get_kmers(sequence,k):
    end_index = k
    start_index=0
    kmer_list = []
    while (end_index<=(len(sequence))):
        kmer_list.append(sequence[(start_index):(end_index)])
        end_index+=1
        start_index+=1
    return(kmer_list)

def compute_kmer_frequencies(sequence, k):
    kmers_list=get_kmers(sequence,k)
    return json.dumps(Counter(kmers_list))

def extract_features(sequence, k=3):
    gc=gc_content(sequence)
    seq_length=len(sequence)
    kmer_json=compute_kmer_frequencies(sequence,k)
    return {"gc_content": gc, "seq_length": seq_length, "kmer_json": kmer_json}
