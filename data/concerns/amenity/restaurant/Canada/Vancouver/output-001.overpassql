[out:json][timeout:30];
area["name:en"="Vancouver"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;