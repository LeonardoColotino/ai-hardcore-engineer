.PHONY: install test eval ingest ingest-seed run
install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

eval:
	python -m evaluation.run

ingest:
	python -m app.rag.ingest

ingest-seed:
	python -m app.rag.ingest --seed

run:
	python -m uvicorn app.main:app --reload
