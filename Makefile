all:

fetch_stats:
	python -m examples.all_shots

predict_outcome:
	python -m analysis.game_outcome.svc_model

# DEBUG purposes
preprocessing:
	python -m analysis.game_outcome.preprocessing