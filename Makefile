aeroway:
	python3 src/find_orphan_trident.py "data/concerns/aeroway" | xargs -I{} python3 src/generate_overpassql.py "{}"

railway:
	python3 src/find_orphan_trident.py "data/concerns/railway" | xargs -I{} python3 src/generate_overpassql.py "{}"

hotel:
	python3 src/find_orphan_trident.py "data/concerns/tourism/hotel" | xargs -I{} python3 src/generate_overpassql.py "{}"

convenience:
	python3 src/find_orphan_trident.py "data/concerns/shop/convenience" | xargs -I{} python3 src/generate_overpassql.py "{}"

park:
	python3 src/find_orphan_trident.py "data/concerns/leisure/park" | xargs -I{} python3 src/generate_overpassql.py "{}"

cafe:
	python3 src/find_orphan_trident.py "data/concerns/amenity/cafe" | xargs -I{} python3 src/generate_overpassql.py "{}"

bar:
	python3 src/find_orphan_trident.py "data/concerns/amenity/bar" | xargs -I{} python3 src/generate_overpassql.py "{}"

hospital:
	python3 src/find_orphan_trident.py "data/concerns/amenity/hospital" | xargs -I{} python3 src/generate_overpassql.py "{}"

museum:
	python3 src/find_orphan_trident.py "data/concerns/tourism/museum" | xargs -I{} python3 src/generate_overpassql.py "{}"

gallery:
	python3 src/find_orphan_trident.py "data/concerns/tourism/gallery" | xargs -I{} python3 src/generate_overpassql.py "{}"

aquarium:
	python3 src/find_orphan_trident.py "data/concerns/tourism/aquarium" | xargs -I{} python3 src/generate_overpassql.py "{}"

temple:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/buddhist" | xargs -I{} python3 src/generate_overpassql.py "{}"

shrine:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/shinto" | xargs -I{} python3 src/generate_overpassql.py "{}"

church:
	python3 src/find_orphan_trident.py "data/concerns/building/church" | xargs -I{} python3 src/generate_overpassql.py "{}"

mosque:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/muslim" | xargs -I{} python3 src/generate_overpassql.py "{}"
