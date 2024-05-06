TARGETS = \
	railway \
	hotel \
	convenience \
	park \
	cafe \
	bar \
	hospital \
	shelter \
	museum \
	gallery \
	aquarium \
	temple \
	shrine \
	church \
	mosque

all: $(TARGETS)

aeroway:
	python3 src/find_orphan_trident.py "data/concerns/aeroway" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

railway:
	python3 src/find_orphan_trident.py "data/concerns/railway" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

hotel:
	python3 src/find_orphan_trident.py "data/concerns/tourism/hotel" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

convenience:
	python3 src/find_orphan_trident.py "data/concerns/shop/convenience" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

park:
	python3 src/find_orphan_trident.py "data/concerns/leisure/park" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

cafe:
	python3 src/find_orphan_trident.py "data/concerns/amenity/cafe" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

bar:
	python3 src/find_orphan_trident.py "data/concerns/amenity/bar" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

hospital:
	python3 src/find_orphan_trident.py "data/concerns/amenity/hospital" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

shelter:
	python3 src/find_orphan_trident.py "data/concerns/amenity/shelter" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

museum:
	python3 src/find_orphan_trident.py "data/concerns/tourism/museum" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

gallery:
	python3 src/find_orphan_trident.py "data/concerns/tourism/gallery" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

aquarium:
	python3 src/find_orphan_trident.py "data/concerns/tourism/aquarium" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

temple:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/buddhist" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

shrine:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/shinto" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

church:
	python3 src/find_orphan_trident.py "data/concerns/building/church" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"

mosque:
	python3 src/find_orphan_trident.py "data/concerns/amenity/place_of_worship/religion/muslim" | grep Seoul | xargs -I{} python3 src/generate_overpassql.py "{}"
