[out:json][timeout:30];
area["name:en"="Lisbon"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;