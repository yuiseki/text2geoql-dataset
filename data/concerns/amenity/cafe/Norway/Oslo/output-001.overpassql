[out:json][timeout:30];
area["name:en"="Oslo"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;