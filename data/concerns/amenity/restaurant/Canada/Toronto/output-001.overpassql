[out:json][timeout:30];
area["name:en"="Toronto"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;