import pandas as pd
import numpy as np
from lingpy import *

from segments.tokenizer import Tokenizer
from functions import remove_spaces, prior_forms, parser2 

def dataPreparer(data="data.tsv", tokenizer="orthography.tsv", parser=parser2):
    """
    This function takes a dataset and prepares it for alignment analysis
    data- the raw tsv data
    tokenizer-a tokenizer that has been semi-manually prepared
    parser- a parser function
    """
    data = pd.read_csv(data, sep="\t", encoding="utf-8")
    list_to_drop=["ID","FRENCH", "ENGLISH_SHORT", "FRENCH_SHORT", "ENGLISH_CATEGORY", 
                  "FRENCH_CATEGORY", "PARSED FORM", "MCF", "RECONSTRUCTION", "NOTE", 
                  "NOTES","Unnamed: 18", "Unnamed: 19", "Unnamed: 20", "Unnamed: 21", 
                  "COGID", "COGIDS", "Unnamed: 24"]
    data = data.drop(list_to_drop, axis=1)
    data["BEFORE_PARSE"] = data.apply(prior_forms, axis=1)  

    if parser is not None:
        data["PARSED"] = data.apply(lambda row: parser(row), axis=1) 

    tk = Tokenizer(tokenizer)
    data["IPA"] = data["BEFORE_PARSE"].apply(lambda x: tk(x, column="IPA") if isinstance(x, str) else x)  
    data["IPA"] = data["IPA"].apply(remove_spaces)  
    data = data[data["POS"].isin (["noun", "verb"])]
  
    data = data[["DOCULECT", "CONCEPT", "IPA"]].dropna(subset=["DOCULECT", "CONCEPT", "IPA"])
    data.replace("", np.nan, inplace=True)
    data = data.dropna(subset=["IPA"])
    data = data.drop(data.loc[(data["CONCEPT"] == "(1Pl subject pronominal)") & (data["DOCULECT"] == "Mombo")].index)

    data = data.drop(data.loc[(data["DOCULECT"] == "Nanga")].index) #there are issues with Nanga data so it is removed for now
 
    return data.to_csv("cleaned_data.tsv", index=False, encoding="utf-8", sep='\t')

def retainer(wl, coverage_number):
    "function for data reduction"
    retained = []
    for language, coverage in wl.coverage().items():
        if coverage > coverage_number:
            retained.append(language)
    return retained

def fullAlign(coverage_number=200):
    "cognate detection function that returns a lexstat object for distance metric calculation"

    dataPreparer()
    wl = Wordlist("cleaned_data.tsv")
    retained = retainer(wl, coverage_number)
    
    new_wl = {0: [c for c in wl.columns]}
    for idx, language in wl.iter_rows("doculect"):
        if language in retained:
            new_wl[idx] = wl[idx]
    new_wl = Wordlist(new_wl)
    
    #cognate detection with full words
    lex = LexStat(new_wl)
    lex.get_scorer(runs=10000)
    lex.cluster(method='lexstat', threshold=0.55, ref='cogid')
    lex.calculate('tree',tree_calc='neighbor',ref='cogid')

    alm=Alignments(lex, ref="cogid")
    alm.align(method="library")
    distance = alm.get_distances(method="lexstat", ref="cogid")
    taxa = alm.taxa
    df=pd.DataFrame(distance, index=taxa, columns=taxa)
    df.to_csv("linguistic_distance.tsv", index=True, encoding="utf-8", sep='\t')
    return df


