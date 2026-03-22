[out:json][timeout:30];
area["name:en"="Toronto"]->.searchArea;
(
  nwr["amenity"="cafe"](area.searchArea);
);
out geom;