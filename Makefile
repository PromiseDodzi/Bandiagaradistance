.PHONY: all prepare install run ungrouped coverage cognates illustrations statistics

all: prepare install run ungrouped coverage cognates illustrations statistics
prepare:
	python prepare_manual_data.py
install:
	pip install -e .
run:
	cldfbench lexibank.makecldf --glottolog="C:/Users/Promise Dodzi Kpoglu/glottolog" --concepticon="C:/Users/Promise Dodzi Kpoglu/concepticon-data" --clts="C:/Users/Promise Dodzi Kpoglu/clts" --glottolog-version=v5.0 --concepticon-version=v3.2.0 --clts-version=v2.3.0 heathdogon

ungrouped:
	edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped"

coverage:
	python coverage.py

cognates:
	python distance.py
illustrations:
	python get_illustrations.py
statistics:
	python get_statistics.py



