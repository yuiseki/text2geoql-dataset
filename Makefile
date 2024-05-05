
church:
	python src/find_orphan_trident.py "data/concerns/building/church" | xargs -I{} python src/generate_overpassql.py "{}"

gallery:
	python src/find_orphan_trident.py "data/concerns/tourism/gallery" | xargs -I{} python src/generate_overpassql.py "{}"
