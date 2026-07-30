from lingpy import Wordlist
import pandas as pd
import collections
from tabulate import tabulate


def get_coverage():

    data = "processed_data/value_cleaned_data.tsv"

    df = pd.read_csv(data,sep=";",low_memory=False,dtype=str).fillna("")
    

    # Required LingPy columns
    df["doculect"] = df["glottoname"].str.replace(" ", "_", regex=False)
    df["concept"] = df["concepticon_gloss"].str.replace(" ", "_", regex=False)
    df["tokens"] = df["cleaned_value_org"]

    # remove rows without a lexical form
    df = df[df["tokens"] != ""]

    # Create LingPy dictionary
    D = {
        0: [
            "doculect",
            "concept",
            "tokens",
            "concepticon_id"
        ]
    }

    for i, row in enumerate(df.itertuples(index=False), start=1):
        D[i] = [row.doculect,row.concept,row.tokens,row.concepticon_id]

    wl = Wordlist(D)

    # Language coverage
    retain = []

    for language, coverage in wl.coverage().items():
        if coverage > 288:
            retain.append(language)

    print(f"Retaining {len(retain)} languages")

    # Restrict languages
    header = D[0]
    new = {0: header}

    for idx in wl:
        if wl[idx, "doculect"] in retain:
            new[idx] = [wl[idx, col] for col in header]

    new_wl = Wordlist(new)

    # Count concept coverage
    concepts = collections.defaultdict(lambda: {k: 0 for k in new_wl.cols})

    for idx in new_wl:
        c = new_wl[idx, "concept"]
        l = new_wl[idx, "doculect"]
        concepts[c][l] = 1

    # Select the 300 best-covered concepts
    sorted_concepts = sorted(concepts,key=lambda x: sum(concepts[x].values()),reverse=True)[:300]


    # Final wordlist
    final = {0: header}

    for idx in wl:
        if (
            wl[idx, "doculect"] in retain
            and
            wl[idx, "concept"] in sorted_concepts
        ):
            final[idx] = [wl[idx, col] for col in header]

    final_wl = Wordlist(final)

    final_wl.output("tsv",filename="processed_data/value_cleaned_data-shortened",prettify=False,ignore="all")

    print(f"\nLanguages : {final_wl.width}")
    print(f"Concepts  : {final_wl.height}")

    table = []

    for language, coverage in final_wl.coverage().items():
        table.append([language,coverage,coverage / final_wl.height])

    print(tabulate(table,headers=["language", "items", "coverage"],floatfmt=".2f"))


if __name__ == "__main__":
    get_coverage()