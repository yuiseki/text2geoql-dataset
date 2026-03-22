[out:json][timeout:30];
area["name:en"="Oslo"]->.searchArea;
(
  nwr["amenity"="restaurant"](area.searchArea);
);
out geom;