.PHONY: all ungrouped coverage cognates

all: ungrouped coverage cognates

ungrouped:
	edictor wordlist --dataset="cldf/cldf-metadata.json" \
		--namespace='{"id": "local_id", "language_id": "doculect", "variety": "variety", "concept_name": "concept","value": "value", "form": "form", "segments": "tokens","plural_segments": "plural_tokens", "comment": "note", "concept_swadesh": "swadesh"}' \
		--name="heathdogon-ungrouped"

coverage:
	python coverage.py

cognates:
	python distance.py



