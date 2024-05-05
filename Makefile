
church:
	python3 src/find_orphan_trident.py "data/concerns/building/church" | xargs -I{} python3 src/generate_overpassql.py "{}"

gallery:
	python3 src/find_orphan_trident.py "data/concerns/tourism/gallery" | xargs -I{} python3 src/generate_overpassql.py "{}"
