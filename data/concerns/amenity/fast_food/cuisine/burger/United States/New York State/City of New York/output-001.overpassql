[out:json][timeout:30];
area["name"="City of New York"]->.searchArea;
(
  nwr["amenity"="fast_food"]["cuisine"="burger"](area.searchArea);
);
out geom;
