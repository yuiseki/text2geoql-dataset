[out:json][timeout:30];
area["name:en"="Zurich"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;