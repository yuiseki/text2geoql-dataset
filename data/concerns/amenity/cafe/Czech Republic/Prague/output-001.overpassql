[out:json][timeout:30];
area["name:en"="Prague"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;