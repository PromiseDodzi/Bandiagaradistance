# Bandiagaradistance
This repository accompanies the paper `On linguistic and geographic distances in the Bandiagara` by Promise Dodzi Kpoglu. The repository contains both the data and source code used in the paper's experiments.

# Data
Data for this paper is derived from Heath et al's "Dogon Comparative Wordlist" from 2016.  
The orginal data curated in CLDF (Cross Linguistic Data Format) is publicly available at the following link: https://github.com/languageorphans/heathdogon.
However, the original data is not morphologically segmented.
The current paper first segments the data after reading the various grammars available on the Dogon languages.  
All files relating to further processing of data are done in manual_data_files

##  Manual_data_files
This folder contains:  
* `utils.py`, a python scrit with morphological segmentation rule
* `functions.py`, a set of functions that process the data
*  `ortho_1.tsv`, an orthography profile for IPA conversion and grapheme standardization
*  `towards_manually_edited.tsv`, a raw data that is a derived version of data before transformation into CLDF


The `prepare_manual_data.py` script in the base folder, calls various functions from `functions.py` in `manual_data_files`, to parse data.  
The output is deposited in the `raw` folder.

## raw
The raw folder contains the original data four datasets, which are crucial to CLDF conversion
NB: CLDF conversion is done using the following commands:
* `pip install -e .`
* `cldfbench lexibank.makecldf --glottolog="address/glottolog" --concepticon="address/concepticon-data" --clts="address/clts" --glottolog-version=v5.0 --concepticon-version=v3.2.0 --clts-version=v2.3.0 heathdogon`
* adress = path on your local machine
  
The `lexibank_heathdogon.py` script in the base folder, takes the `manually-edited.csv` data, and the original data also available at https://github.com/languageorphans/heathdogon, and merges them.  
The output is `forms.csv` which is found in the `cldf` folder.

## cldf
Thus `forms.csv` has morphologically segmented data where both original data and `manually-edited.csv`  entries are same.  
Where forms exists in `manually-edited.csv`, but not in original data, there also is a segmened data
Finally, where forms exist in original data, but not in `manually-edited.csv`, original data is concerved.
More importantly, `cldf-metadata.json` contains the metadata description of the result of the cldf conversion

The `edictor` folder, `etc` folder, and `lexibank_heathdogon.egg-info` contain files related to the cldf conversion process.

After cldf conversion, the command line instruction  
`edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped"`
is used to take the CLDF dataset (from the metadata file) and using edictor to process it into a wordlist.  
The output is `heathdogon-ungrouped` in the root folder.

## matrices
This folder contains the geographical data `Geodata.csv` and a linguistics distance matrix 'linguistic_distance_matrix.csv'.
The linguistic distance matrix is obtained after linguistic data is filtered by running 'coverage.py', and then `distance.py`

# Illustrations
This folder contains all the graphs and illustrations contained in the paper.
These are obtained from running `get_illustrations.py` in the root folder

# Command line displays
All statistics in the paper can be obtained by running `get_statistics.py`.  
This displays all statistics

# Commands
Prior to running the following commands, clone this repository and run pip install -r requirements.txt

* `python prepare_manual_data.py`, runs the segmentation rule 'utils.py' on manually processed data by calling on various functions in 'functions.py' and outputs `manually-edited.csv` into the `raw` folder.
* `pip install -e .` to install all dependencies for cldf data conversion
* run cldfbench lexibank.makecldf command by replacing address in the following command with a path to glottolog, concepticon and clts - which can be downloaded
  `cldfbench lexibank.makecldf --glottolog="address/glottolog" --concepticon="address/concepticon-data" --clts="address/clts" --glottolog-version=v5.0 --concepticon-version=v3.2.0 --clts-version=v2.3.0 heathdogon`
* convert cldf data into wordlist by running `edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped`
* `python coverage.py`, filters data according to coverage by favoring breath.
* `python distance.py`, undertakes automatic cognate detction, cognate alignment and linguistic distance calculation, and outputs results into `matrices folder`
* `python get_illustrations.py`, undertakes calculates and outputs all graphs and illustrations used in the paper.
* `python get_statistics.py`, prints all statistics to the command line
