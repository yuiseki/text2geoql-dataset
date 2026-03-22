[out:json][timeout:30];
area["name:en"="Prague"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;