[out:json][timeout:30];
area["name:en"="Vienna"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;