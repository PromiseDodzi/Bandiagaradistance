
from lingpy.compare.partial import Partial
from lingpy import Alignments, Wordlist, LexStat
import pandas as pd
import os


def clean_data():
    input_file = "processed_data/value_cleaned_data-shortened.tsv"
    output_file = "processed_data/value_cleaned_data-clean.tsv"

    df = pd.read_csv(input_file, sep="\t")

    bad_rows = []

    for i, row in df.iterrows():
        try:
            temp = pd.DataFrame([row])
            temp.to_csv("processed_data/_temp.tsv", sep="\t", index=False)

            LexStat("processed_data/_temp.tsv", ref="tokens")

        except Exception:
            bad_rows.append(i)

    print("Removing rows:", bad_rows)

    # delete problematic rows
    df_clean = df.drop(bad_rows)
    df_clean.to_csv(output_file, sep="\t", index=False)

    print("Saved:", output_file)
    print("Removed", len(bad_rows), "rows")


def get_distance():
    

    data="processed_data/value_cleaned_data-clean.tsv"
    wl = Wordlist(data)
    print(wl.header)


    columns = [c for c in wl.columns] + ["cogid"]
    lex = LexStat(data)
    try:
        lex.get_scorer(method="markov", runs=200, rands=200)
    except MemoryError:
        print("MemoryError during LexStat scoring: retrying with smaller parameters")
        lex.get_scorer(method="markov", runs=100, rands=100)
    lex.cluster(ref="cogid", method="lexstat", threshold=0.55, cluster_method="upgma")

    # get new wordlist with cognates 
    new_wl = {0: columns}
    for idx in lex:
        new_wl[idx] = [lex[idx, c] for c in columns]


    alms = Alignments(lex, transcription="tokens", ref="cogid")
    alms.align(method="library")

    alms.output("tsv", filename= data[:-4] + "-aligned", ignore="all",prettify=False)

    distance = alms.get_distances(method="lexstat", ref="cogid")
    taxa = alms.taxa
    df=pd.DataFrame(distance, index=taxa, columns=taxa)

    base_dir = os.getcwd()  
    output_dir = os.path.join(base_dir,"matrixes")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "linguistic_distance_matrix.csv")

    return df.to_csv(output_path, index=True)

if __name__== "__main__":
    clean_data()
    get_distance()
