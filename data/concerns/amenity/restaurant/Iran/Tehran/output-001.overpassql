[out:json][timeout:30];
area["name:en"="Tehran"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;